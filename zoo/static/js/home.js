jQuery(function($) {
    // Example links type in the search box, then submit
    var input = $('#q');
    var submit = input.parents('form:first').find(':submit');
    $('.examples a').click(function() {
        input.focus();
        animateTextEntry($(this).text());
        return false
    });
    function animateTextEntry(text) {
        input.val('');
        var i = 1;
        var timeout = setInterval(function() {
            if (input.val() != text) {
                input.val(text.slice(0, i));
                i++;
            } else {
                clearTimeout(timeout);
                submit.addClass('active');
                setInterval(function() {
                    submit.removeClass('active');
                    submit.click();
                }, 300);
            }
        }, 25);
    }
});
