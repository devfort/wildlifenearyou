function anyEmptyOnes() {
    return jQuery('.see-more-animals div:visible :text').filter(function() {
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
                $('div.see-more-animals .and-a').show();
            } else {
                // Clone an existing .and-a
                var and_a = $(
                    'div.see-more-animals .and-a'
                ).eq(0).clone();
                var unused_id = unusedSawId();
                and_a.find('input').val('').attr({
                    'id': unused_id,
                    'name': 'saw'
                });
                and_a.find('label').attr('for', unused_id);
                and_a.insertBefore('.see-more-animals :submit');
                setupSawBoxes();
            }
        }
    }
    function setupSawBoxes() {
        $('div.see-more-animals input[name^=saw]').unbind('.doweneed').bind(
            'keyup.doweneed', doWeNeedMoreBoxes
        ).autocomplete('/autocomplete/species/', {
            dataType: 'json',
            selectFirst: true,
            width: 400,
            formatItem: function(item) {
                var result = item.common_name;
                if (item.scientific_name) {
                    result += ', ' + item.scientific_name;
                }
                if (item.num_sightings) {
                    result += ' (seen ' + item.num_sightings + ' times)';
                }
                return result;
            },
            formatResult: function(item) {
                return item.common_name;
            },
            parse: function(data) {
                return $.map(data, function(row) {
                    return {
                        data: row,
                        value: row.common_name,
                        result: row.common_name
                    }
                });
            }
        });
    }
    // Set up the I saw a form bit
    if (anyEmptyOnes()) {
        $('div.see-more-animals .and-a').hide()
    }
    setupSawBoxes();
    doWeNeedMoreBoxes();
    
    // Since we're using autocomplete, the form should not submit unless the 
    // button is directly clicked.
    $('div.see-more-animals form').submit(function() {
        return false;
    });
    // Problem: if you hit "enter" in one of the fields, Firefox fires the 
    // click() event on the first submit button in the form. So, to create 
    // a submit button that can be clicked to submit the form WITHOUT it 
    // being magically clicked when you hit enter inside another field, you 
    // need to clone the original submit button, hide it and set up the 
    // click behaviour on that clone. Crazy but it works.
    var submit = $('div.see-more-animals :submit');
    var submit2 = submit.clone();
    submit2.insertAfter(submit);
    submit.hide();
    submit2.click(function() {
        $('div.see-more-animals form')[0].submit();
    });
});
