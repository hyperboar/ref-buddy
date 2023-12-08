document.getElementById('board-send-btn').addEventListener('click', (e) =>
{
    if (selection == null || selection.selectedIds.length === 0) { return }

    const ids = selection.selectedIds.join(',')

    const btn = e.currentTarget
    const board_id = document.getElementById('boards').value
    const url = btn.getAttribute('data-url')
    fetchAndSimpleFeedback(`${url}?b-id=${board_id}&image-id=${ids}`, btn)
})
document.getElementById('board-send-close-btn').addEventListener('click', () =>
{
    document.getElementById('boards-popup').classList.add('vis-hide')
    document.getElementById('board-send-btn').classList.remove('op-success', 'op-fail')
})