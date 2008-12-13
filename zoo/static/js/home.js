jQuery(function($) {
    
    /* Example links type in the search box, then submit */
    
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
        infobox.find('div.info').html(a.attr('origtitle'));
    });
    
    photostrip.mouseout(function() {
        infobox.hide();
    });
});
