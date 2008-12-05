function anyEmptyOnes() {
    return jQuery('#see-more-animals div:visible :text').filter(function() {
        return $(this).val() == '';
    }).length > 0;
}

function unusedSawId() {
    var i = 1;
    var saw_id = 'saw_' + i;
    while ($('#' + saw_id).length) {
        i += 1;
        saw_id = 'saw_' + i;
    }
    return saw_id;
}

jQuery(function($) {
    function doWeNeedMoreBoxes() {
        var $this = $(this);
        if ($this.val()) {
            // Only do something if this is the last empty one
            if (anyEmptyOnes()) {
                return;
            }
            if (!$this.parent().hasClass('and-a')) {
                $('div#see-more-animals .and-a').show();
            } else {
                // Clone an existing .and-a
                var and_a = $(
                    'div#see-more-animals .and-a'
                ).eq(0).clone();
                var unused_id = unusedSawId();
                and_a.find('input').val('').attr({
                    'id': unused_id,
                    'name': 'saw'
                });
                and_a.find('label').attr('for', unused_id);
                and_a.insertBefore('#see-more-animals :submit');
                setupSawBoxes();
            }
        }
    }
    function setupSawBoxes() {
        $('div#see-more-animals input[name^=saw]').unbind('keyup').keyup(
            doWeNeedMoreBoxes
        );
    }
    // Set up the I saw a form bit
    if (anyEmptyOnes()) {
        $('div#see-more-animals .and-a').hide()
    }
    setupSawBoxes();
    doWeNeedMoreBoxes();
});
