

with (open('tags', 'r') as f):
    parts = [line.strip().split(',') for line in f if len(line.strip()) > 0]
    ids = [(int(p[2].strip()), int(p[0].strip())) for p in parts]

    for r, ai in ids:
        print(f'insert into tags_ai_to_tags (real_id, ai_id) values ({r}, {ai}) ', end='')
        print(f'ON CONFLICT(real_id, ai_id) DO NOTHING;')

    print(len(ids))