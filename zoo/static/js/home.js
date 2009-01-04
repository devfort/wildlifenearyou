jQuery(function($) {
    
    /* Example links type in the search box, then submit */
    
    var input = $('#q');
    var searchSubmit = input.parents('form:first').find(':submit');
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
                searchSubmit.addClass('active');
                setInterval(function() {
                    searchSubmit.removeClass('active');
                    searchSubmit.click();
                }, 300);
            }
        }, 25);
    }
    
    /* Photostrip details viewer */
    
    // Construct an arrow using CSS border hacks
    var arrow = $('<div><div></div><div></div></div>').css('height', '10px');
    arrow.find('div:first').css({
        'float': 'left',
        'border-bottom': '10px solid #6D9053',
        'border-left': '10px solid transparent',
        'height': '1',
        'width': '1'
    }).end().find('div:last').css({
        'float': 'left',
        'border-bottom': '10px solid #6D9053',
        'border-right': '10px solid transparent',
        'height': '0',
        'width': '0'
    });
    
    var photostrip = $('ul.photostrip');
    // Construct the photo information box itself
    var infobox = $('<div><div class="info"></div></div>').css({
        'width': 250,
        'height': 30,
        'position': 'absolute',
        'top': photostrip.offset().top + photostrip.height() + 2,
        'left': 20,
        'text-align': 'left'
    }).appendTo(document.body).hide();
    infobox.find('div.info').css({
        'border': '1px solid #6D9053',
        'background-color': '#C6DDAB',
        'color': 'black',
        'padding': '2px'
    }).html('HEllo').before(arrow);
    
    // We need to supress the default browser titles, but we use them to 
    // figure out what is currently moused over - so first we need to stash 
    // the titles in an origtitle attribute (this is safe since it's only a 
    // string, if it was a complex object we would use jQuery.data())
    photostrip.find('a').each(function() {
        var $this = $(this);
        $this.attr('origtitle', $this.attr('title'));
        $this.attr('title', '');
        $this.find('img').attr('alt', ''); // To supress in IE
    });

    // Cache window_width but update on resize
    var window_width = $(window).width();
    $(window).resize(function() {
        window_width = $(window).width();
        // Might need to reposition infobox.top too in extreme resizes
        infobox.css('top', photostrip.offset().top + photostrip.height() + 2);
    });
    
    photostrip.mousemove(function(ev) {
        // Left should always be between 0 and (window_width - infobox width)
        // Are we over a link?
        var a = $(ev.target).parents('a');
        if (!a.length) {
            infobox.hide();
            return;
        }
        infobox.show();
        var left = Math.max(10, ev.pageX - 10);
        if (left > window_width - (infobox.width() + 10)) {
            left = window_width - (infobox.width() + 10);
            // BUT now the arrow needs to move along a bit
            arrow.css('margin-left', Math.min(
                infobox.width() - 20, ev.pageX - left
            ));
        } else {
            arrow.css('margin-left', 0);
        }
        infobox.css('left', left);
        infobox.css('top', photostrip.offset().top + photostrip.height() + 2);
        infobox.find('div.info').html(a.attr('origtitle'));
    });
    
    photostrip.mouseout(function() {
        infobox.hide();
    });
    
    // Set up the autocomplete for the "Add a trip to..." box
    $('input#search-place').autocomplete('/places/autocomplete/', {
        dataType: 'json',
        selectFirst: true,
        formatItem: function(item) {
            return item.name;
        },
        parse: function(data) {
            return $.map(data, function(row) {
                return {
                    data: row,
                    value: row.name,
                    result: row.name
                }
            });
        }
    }).bind('result', function(ev, result) {
        var url = 'http://' + location.host + result.url;
        window.location = url;
    });
    // Since we're using autocomplete, the form should not submit unless the 
    // button is directly clicked.
    $('input#search-place').parents('form').submit(function() {
        return false;
    });
    // Problem: if you hit "enter" in one of the fields, Firefox fires the 
    // click() event on the first submit button in the form. So, to create 
    // a submit button that can be clicked to submit the form WITHOUT it 
    // being magically clicked when you hit enter inside another field, you 
    // need to clone the original submit button, hide it and set up the 
    // click behaviour on that clone. Crazy but it works.
    var addTripSubmit = $('input#search-place').parents('form').find(':submit');
    var submit2 = addTripSubmit.clone();
    submit2.insertAfter(addTripSubmit);
    addTripSubmit.hide();
    submit2.click(function() {
        $('input#search-place').parents('form')[0].submit();
    });
});
