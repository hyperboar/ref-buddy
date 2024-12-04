import json
import os
from datetime import datetime

from flask import Blueprint, request, abort, render_template, redirect, jsonify
from models.models_lump import Tag, Session, ImageMetadata, TagSet, TagAi, ImageTagAi, TagAiToTag, ImageTag
from sqlalchemy.sql import exists
from sqlalchemy import inspect

routes_tags_ai = Blueprint('routes_tags_ai', __name__)


#region ---- JSON API ----
@routes_tags_ai.route('/tags-ai/suck-folder-in')
def suck_in_all_tags_in_folder():
    path = os.path.join(os.getcwd(), 'autotag_fetcher', 'output_export_2d.json')
    session = Session()

    files = os.listdir(path)
    files_count = 0
    max = len(files)
    for file in files:
        print(f"({files_count}/{max}) Checking file {os.path.join(path, file)}...", flush=True)
        with open(os.path.join(path, file), 'r') as f:
            files_count += 1

            data = json.load(f)

            # import new tags
            count_new = 0
            for tag in data['tags']:
                query = session.query(exists().where(TagAi.tag == tag))
                has_tag = session.scalar(query)
                if has_tag: continue
                count_new += 1
                session.add(TagAi(tag=tag))

            if count_new > 0:
                session.commit()

            # build mapping for internal tag id to db tag id
            tags_to_db = {}
            for i in range(len(data['tags'])):
                tag_id = session.query(TagAi.id).filter(TagAi.tag == data['tags'][i]).one()[0]
                tags_to_db[str(i)] = tag_id

            # import image-tag + rating
            count_new = 0
            for img in data['images']:
                img_id = int(img['id'])
                timestamp = datetime.fromtimestamp(int(img['timestamp']))
                for key, value in img['tags'].items():
                    result = session.merge(ImageTagAi(image_id=img_id, tag_id=tags_to_db[key], rating=value, imported_at=timestamp))
                    if inspect(result).pending:
                        count_new += 1
            if count_new > 0:
                session.commit()

    session.close()
    return jsonify({'ok': f'{path}'})

@routes_tags_ai.route('/tags-ai/update-mapped-tags')
def update_mapped_tags():
    session = Session()

    mapping = session.query(TagAiToTag).all()

    count_new = 0
    new_tags = {}
    for m in mapping:
        img_ids = [im[0] for im in session.query(ImageTagAi.image_id).filter(ImageTagAi.tag_id == m.ai_id).all()]
        for img_id in img_ids:
            result = session.merge(ImageTag(image_id=img_id, tag_id=m.real_id, by_ai=1))
            if inspect(result).pending:
                if not m.real_tag.tag in new_tags:
                    new_tags[m.real_tag.tag] = 0
                new_tags[m.real_tag.tag] += 1
                count_new += 1

        print(f'new for {m.real_tag.tag}:{m.ai_tag.tag} {count_new}')
        if count_new > 0:
            count_new = 0
            session.commit()

        # print(m.real_tag.tag)

    print(f'new {count_new}')
    # session.rollback()
    # session.commit()
    session.close()
    return jsonify({'ok': f'{count_new}', 'stat': new_tags})

@routes_tags_ai.route('/tags-ai/all')
def get_all_tags():
    session = Session()
    tags = session.query(Tag).all()
    out = {'tags': []}
    for tag in tags:
        out['tags'].append({'id': tag.id, 'name': tag.tag})
    session.close()
    return jsonify(out)

@routes_tags_ai.route('/tags-ai/image/single/<int:image_id>')
def image_tags_single(image_id):
    session = Session()
    im = session.get(ImageMetadata, image_id)
    tags = [{'color': it.tag.color.hex, 'name': it.tag.tag} for it in im.tags]
    out = [{'image_id': image_id, 'tags': tags}]
    session.close()
    return jsonify(out)

@routes_tags_ai.route('/tags/image/bulk', methods=['POST'])
def image_tags_bulk():
    if request.method != 'POST':
        return abort(404, 'Should be GET')

    json = request.get_json()
    image_ids = json['image_ids'] if 'image_ids' in json else []

    session = Session()
    data = {}
    for img in session.query(ImageMetadata).filter(ImageMetadata.image_id.in_(image_ids)).all():
        data[img.image_id] = [t.tag.tag for t in img.tags]

    return jsonify(data)

@routes_tags_ai.route('/tags/set-list')
def tag_set_list():
    session = Session()
    out = [{'alias': s.set_alias, 'name': s.set_name, 'tags': s.tag_list} for s in session.query(TagSet).order_by(TagSet.set_name).all()]
    session.close()
    return jsonify(out)

#endregion ---- JSON API ----


#region ---- CRUD TAG ----

@routes_tags_ai.route('/tags-ai')
def show_tags():
    session = Session()
    tags = session.query(Tag).order_by(Tag.color_id, Tag.tag).all()
    return render_template('crud/tpl_tags_list.html', tags=tags)

@routes_tags_ai.route('/tags-ai/add', methods=['GET', 'POST'])
def add_tag():
    if request.method == 'POST':
        session = Session()
        tag = request.form['tag'].strip()
        color_id = int(request.form['color'].strip())
        new_tag = Tag(tag=tag, color_id=color_id)
        session.add(new_tag)
        session.commit()
        return redirect('/tags')
    return render_template('crud/tpl_tags_add.html')

@routes_tags_ai.route('/tags-ai/edit/<int:tag_id>', methods=['GET', 'POST'])
def edit_tag(tag_id):
    session = Session()
    tag = session.get(Tag, tag_id)
    if request.method == 'POST':
        tag.tag = request.form['tag'].strip()
        tag.color_id = int(request.form['color'].strip())
        session.commit()
        return redirect('/tags')
    return render_template('crud/tpl_tags_edit.html', tag=tag)

@routes_tags_ai.route('/tags-ai/delete/<int:tag_id>', methods=['POST'])
def delete_tag(tag_id):
    session = Session()
    tag = session.get(Tag, tag_id)
    session.delete(tag)
    session.commit()
    return redirect('/tags-ai')

#endregion ---- CRUD TAG ----