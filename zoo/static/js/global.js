jQuery(function($) {
	// add JavaScript class for styling
	$('body').addClass('hasJS');


	// add classes to odd table rows
	$('table tbody tr:nth-child(odd)').addClass('odd');
	
	//	Automatically clear default text in input fields when they are focused
	$("input[type='text']").focus(function() {
		if (($(this).val() == this.defaultValue) && ($(this).hasClass('remove-default'))) {
			$(this).val('');
		}
	});
	//	Reinstate the default value if nothing has been entered.
	$("input[type='text']").blur(function() {
		if (($(this).val() == '') && ($(this).hasClass('remove-default'))) {
			$(this).val(this.defaultValue);
		}
	});

	//	Make the targets of internal links toggleable.
	$('a.toggler').each(function() {
		//	Get the id of the target of each internal link.
		var selector = $(this).attr('href');
		if ($(selector)) {
			$(selector).toggle();
			//	When an internal link is clicked, toggle the display of the target.
			$(this).click(function() {
				var selector = $(this).attr('href');
				$(selector).css({'overflow':'hidden'});
				$(selector).slideToggle('fast');
				$(this).toggleClass('displaying');
				return false;
			});
		}
	});
	
	// Toggleability of inputs (should work on radio and checkbuttons)
	$('input.toggler').each(function() {
		
		//expecting sourcecode that looks like:
		/*
		<fieldset class="togglerContainer">
			<div>
				<label for="billing-yes">
					<input name="billing-copy" value="yes" type="radio" id="billing-yes" checked="checked" /> 
					Yes - copy over my delivery address
				</label>
			</div>
			<div>
				<label for="billing-no">
					<input name="billing-copy" value="no" type="radio" class="toggler" id="billing-no"/> 
					No - Ill add my billing address
				</label>
				<div class="dependent">
					<label for="billing-street">Street and house</label>
					<input type="text" class="text" name="billing-street" id="billing-street" />
				</div>
			</div>
		</fieldset>
		*/
		// the input can be a sibling of the dependent too.
		// this should also work with checkboxes
		
		// any radio or checkbox with a class of toggler 
		// indicates its group has dependent elements embedded.
		if(($(this).attr('type') == 'radio') || ($(this).attr('type') == 'checkbox')) {
			
			// hide all dependants
			$($(this).parents('.togglerContainer')[0]).find('.dependent').hide();
			
			// get all the corresponding inputs
			var inputgroup = $(this).attr('name');
			
			// check for default value and show dependents
			$('[name="'+inputgroup+'"]').each(function(){
				
				if(this.checked) {
					var dependentContainer; // jquery object
					// show this dependent child
					if($(this.parentNode).find('.dependent').length > 0) {
						// our input has dependent code which is a sibling of our input
						dependentContainer = $(this.parentNode);
					} else if($(this.parentNode.parentNode).find('.dependent').length > 0) {
						// our input might be inside another container like
						// a label, go one up and look
						dependentContainer = $(this.parentNode.parentNode);
					}	
				
					if(dependentContainer) {
						// show the one we want
						dependentContainer.find('.dependent').show();
					}
				}
			});
			
			// assign a click action to every element in that group
			$('[name="'+inputgroup+'"]').click(function() {
				// have clicked on an input in a toggle group.
				
				var togglerContainer = $(this).parents('.togglerContainer')[0];
				var dependentContainer; // jquery object
				
				
				// show this dependent child
				if($(this.parentNode).find('.dependent').length > 0) {
					// our input has dependent code which is a sibling of our input
					dependentContainer = $(this.parentNode);
				} else if($(this.parentNode.parentNode).find('.dependent').length > 0) {
					// our input might be inside another container like
					// a label, go one up and look
					dependentContainer = $(this.parentNode.parentNode);
				}
				
				if(dependentContainer) {
					// if there are things we want to show
					//console.log('there are things we want to show')
					
					// if the thing that we want to show is not already showing
					if(!dependentContainer.find('.dependent:visible').length) {
						// hide all other dependent childeren
						$(togglerContainer).find('.dependent').slideUp('slow');
						// show the one we want
						dependentContainer.find('.dependent').slideDown('slow');
					}
				} else {	
					// hide all other dependent childeren
					$(togglerContainer).find('.dependent').slideUp('slow');
				}
			});
		}

	});
	
	// addSizes was written by Natalie Downe 
	// http://natbat.net/2008/Aug/27/addSizes/
	// Copyright (c) 2008, Natalie Downe under the BSD license
	// http://www.opensource.org/licenses/bsd-license.php
	
	$('a[href$=".pdf"], a[href$=".doc"], a[href$=".mp3"], a[href$=".jpg"], a[href$=".png"], a[href$=".swf"], a[href$=".zip"], a[href$=".ogg"], a[href$=".m4u"]').each(function(){
		// looking at the href of the link, if it contains pdf, doc, zip, mp3, ogg, m4u, jpg, png, swf
		var link = $(this);
		var bits = this.href.split('.');
		var type = bits[bits.length -1];
		
		var url= "http://json-head.appspot.com/?url="+encodeURIComponent (this.href)+"&callback=?";
	
		// then call the json thing and insert the size back into the link text
		 $.getJSON(url, function(json){
			if(json.ok && json.headers['Content-Length']) {
				var length = parseInt(json.headers['Content-Length'], 10);
				
				// divide the length into its largest unit
				var units = [
					[1024 * 1024 * 1024, 'GB'],
					[1024 * 1024, 'MB'],
					[1024, 'KB'],
					[1, 'bytes']
				];
				
				for(var i = 0; i < units.length; i++){
					
					var unitSize = units[i][0];
					var unitText = units[i][1];
					
					if (length >= unitSize) {
						length = length / unitSize;
						// 1 decimal place
						length = Math.ceil(length * 10) / 10;
						var lengthUnits = unitText;
						break;
					}
				}
				
				// insert the text directly after the link and add a class to the link
				// note: if you want to insert the size into the link rather than after it change the following 'after' to 'append'
				link.after(' (' + type + ' ' + length + ' ' + lengthUnits + ')');
				link.addClass(type);
			}
		});
	});
});


/* Funky feedback form effect */
jQuery(function($) {
    // Don't add it if we are already on the /feedback/ page
    if (location.pathname == '/feedback/') {
        return;
    }
    
    var feedback_showing = false;
    function hideFeedback() {
        $('#ajax-feedback-form').slideUp('fast', function() {
            $('#ajax-feedback-form').remove();
            feedback_showing = false;
        });
        return false;
    }
    
    function wireUpForm(div) {
        // Hook up the 'cancel' button
        div.find('input[name=close]').click(hideFeedback);
        // Wire up the form to do an Ajax submit
        div.find('form').submit(function() {
            var data = $(this).serialize(); // A query string style thing
            $.ajax({
                'url': this.action,
                'type': 'POST',
                'data': data,
                'success': function(html) {
                    var height = div.height();
                    var newDiv = $(html);
                    div.replaceWith(newDiv);
                    wireUpForm(newDiv);
                    var newHeight = newDiv.height();
                    /* If does NOT contain an errorlist, close after a delay */
                    if (!newDiv.find('ul.errorlist').length) {
                        setTimeout(function() {
                            newDiv.slideUp('slow', function() {
                                newDiv.remove();
                                feedback_showing = false;
                            });
                        }, 2000);
                    }
                },
                'error': function() {
                    alert('Your feedback could not be recorded');
                    div.remove();
                    feedback_showing = false;
                }
            });
            return false;
        });
    }
    
    $('#feedback-link').click(function() {
        if (feedback_showing) {
            hideFeedback();
            return false;
        }
        // Not showing; show the feedback form
        feedback_showing = true;
        $.get(this.href, function(html) {
            var div = $(html).hide().insertAfter('.header').slideDown('fast');
            wireUpForm(div);
        });
        return false;
    });

    $('#jump_to_form').each(function() {
        var elem_name = '#form-' + $(this).val();
	$('html,body').animate({scrollTop: $(elem_name).offset().top + 350}, 500); 
    });
});


jQuery(window).load(function() {
	// Crazyweird fix lets us style abbr using CSS in IE - do NOT run onDomReady, must be onload
	document.createElement('abbr');
});

/* Get Firebug to work - 
   http://www.codecouch.com/2008/10/referenceerror-console-is-not-defined/ */
if (window['loadFirebugConsole']) {
	window.loadFirebugConsole();
} else {
	if (!window['console']) {
		window.console = {};
		window.console.info = alert;
		window.console.log = alert;
		window.console.warn = alert;
		window.console.error = alert;
	}
}

