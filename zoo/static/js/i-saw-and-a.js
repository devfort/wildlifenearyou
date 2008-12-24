console = window.loadFirebugConsole();

function anyEmptyOnes() {
    return jQuery('.see-more-animals :text').filter(function() {
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
    return i;
}

jQuery(function($) {
    
    function ensureFirstContainerUsesISawA(form) {
        form.find('div.container:first').find(
            'strong.label:first,label:first'
        ).text('I saw a');
    }
    
    function addAnotherBoxIfNeeded() {
        console.log('addAnotherBoxIfNeeded');
        if (anyEmptyOnes()) {
            console.log('There are some empty ones');
            return;
        }
        // Clone an existing .and-a
        var and_a = $(
            'div.see-more-animals .and-a:last'
        ).clone();
        var unused_id = unusedSawId();
        and_a.find(':text').val('').attr({
            'id': 'saw_' + unused_id,
            'name': 'saw.' + unused_id + '.s'
        }).removeClass('is-setup');
        and_a.find('label').attr('for', 'saw_' + unused_id);
        and_a.insertBefore('.see-more-animals :submit:last');
        setupSawBoxes();
    }
    function setupSawBoxes() {
        console.log('setupSawBoxes');
        $('div.see-more-animals :text[name^=saw]').each(function() {
            var input = $(this);
            if (input.hasClass('is-setup')) {
                return true;
            }
            input.addClass('is-setup');
            input.keyup(runTheSearch);
        }).unbind('.doweneed').bind('keyup.doweneed', addAnotherBoxIfNeeded);
    }
    
    function runTheSearch(ev) {
        console.log('runTheSearch');
        var input = $(ev.target);
        var xhr = input.data('xhr');
        if (xhr) {
            // Cancel previous request
            xhr.abort();
        }
        if (input.val().length < 3) {
            return;
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
                
                div.find('div:first').height(
                    Math.min(200, div.find('ul:first').height())
                );
                
                // Set up the event handlers
                div.find('ul ul li').css({
                    'cursor': 'pointer'
                }).click(function() {
                    var select_id = $(this).attr('id');
                    var name = $.trim($(this).find('h6').clone().find(
                        'span'
                    ).remove().end().text());
                    div.remove();
                    var container = input.parents('div.container');
                    var ltext = container.find('label').text();
                    var inputname = input.attr('name');
                    var hiddenname = inputname.replace('.s', '.o');
                    var inputid = 'saw_' + inputname.replace(
                        'saw.', ''
                    ).replace('.s', '');
                    container.empty();
                    container.html(
                        '<strong class="label">' + ltext + '</strong> ' + 
                        '<span class="species-name">' + name + '</span>' +
                        '<input id="' + inputid + '" type="hidden" name="' + 
                            inputname + '" value="' + name + '">' +
                        '<input type="hidden" name="' + hiddenname + 
                            '" value="' + select_id + '">'
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
                });
                div.find('a.record-instead').click(function() {
                    // Record that they said 'as-is' here
                    var hiddenname = input.attr('name').replace('.s', '.o');
                    input.parents('div.container').append($(
                        '<input type="hidden" name="' + hiddenname + 
                            '" value="as-is" />'
                    ));
                    div.remove();
                    return false;
                });
            }
        );
        input.data('xhr', xhr);
    }
    $('div.see-more-animals input[name^=saw]').unbind('.doweneed').bind(
        'keyup.doweneed', addAnotherBoxIfNeeded
    )
    setupSawBoxes();
    addAnotherBoxIfNeeded();
    
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
