$heartIcon = $('.fa-heart')

$heartIcon.on('click', async (evt) => {
    let msgId = $(evt.target).data('msgid')
    resp = await axios.post(`/messages/${msgId}/likes`)
    toggleIcon($(evt.target))
})

function toggleIcon($icon) {
    if($icon.hasClass('far')) {
        $icon.removeClass('far')
        $icon.addClass('fas')
    } else {
        $icon.removeClass('fas')
        $icon.addClass('far')
    }
}