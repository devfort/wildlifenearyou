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
                setupSawBoxes();
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
        $('div.see-more-animals input[name^=saw]').each(function() {
            var input = $(this);
            if (input.hasClass('is-setup')) {
                return true;
            }
            input.addClass('is-setup');
            input.keyup(runTheSearch);
        });
    }
    function runTheSearch(ev) {
        var input = $(ev.target);
        var xhr = input.data('xhr');
        if (xhr) {
            // Cancel previous request
            xhr.abort();
        }
        if (input.val().length < 3) {
            return;
        }
        
        function ensureFirstContainerUsesISawA(form) {
            form.find('div.container:first').find(
                'strong.label:first,label:first'
            ).each(function() {
                $(this).text('I saw a');
            });
        }
        
        // Fire off the search
        var xhr = $.get('/autocomplete/species/' + PLACE_ID + '/?q=' + input.val(), 
            function(html) {
                $('.species-autocomplete').remove();
                var div = $(html);
                // Display the div position absolute by the input box */
                div.css({
                    'position': 'absolute',
                    'top': input.offset().top + input.outerHeight() - 2,
                    'left': input.offset().left,
                    'width': 450
                }).appendTo(document.body);
                // Set up the event handlers
                div.find('ul ul li').css({
                    'cursor': 'pointer'
                }).click(function() {
                    var search_id = $(this).attr('id');
                    var name = $.trim($(this).find('h6').clone().find(
                        'span'
                    ).remove().end().text());
                    div.remove();
                    var container = input.parents('div.container');
                    var ltext = container.find('label').text();
                    container.empty();
                    container.html(
                        '<strong class="label">' + ltext + '</strong> ' + 
                        '<span class="species-name">' + name + '</span>'
                    );
                    var remove = $(
                        '<a class="meta" href="#">(remove)</a>'
                    ).click(function() {
                        var form = container.parents('form:first');
                        container.remove();
                        ensureFirstContainerUsesISawA(form);
                        return false;
                    }).appendTo(container.find('span.species-name'));
                });
                div.find('a.close').click(function() {
                    div.remove();
                    return false;
                })
                /*
                var ul = $('<ul></ul>').css('clear', 'both');
                $.each(list, function() {
                    var li = $('<li></li>');
                    li.text(this.common_name + ', ' + this.scientific_name);
                    li.appendTo(ul);
                    if (this.photo) {
                        $(
                            '<img width="45" src="' + this.photo + '" />'
                        ).appendTo(li);
                    }
                });
                ul.insertAfter(input);
                */
            }
        );
        input.data('xhr', xhr);
    }
    $('div.see-more-animals input[name^=saw]').unbind('.doweneed').bind(
        'keyup.doweneed', doWeNeedMoreBoxes
    )
    /*
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
    */
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
