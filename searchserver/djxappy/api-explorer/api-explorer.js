jQuery(function($) {
	// Show the API explorer (it's hidden by default as it fails without JS)
	$('#api-explorer').show();
	
	$.history.init(loadUrl); // The history plugin enables the back button
	$('form').submit(function() {
		$.history.load($('input[name=url]').val());
		return false;
	});
	
	// Set up show/hide toggle behaviour for API examples
	$('<a href="#" class="hide"> [Hide]</a>').click(function() {
		var a = $(this);
		if (a.hasClass('hide')) {
			a.removeClass('hide');
			a.addClass('show');
			a.text(' [Show]');
			$('#examples').hide('fast');
		} else {
			a.removeClass('show');
			a.addClass('hide');
			a.text(' [Hide]');
			$('#examples').show('fast');
		}
		return false;
	}).css({
		'font-size': '0.6em',
		'text-decoration': 'none'
	}).appendTo($('h2'));
	
	function loadUrl(url) {
		if (!url) {
			return; // loadUrl called with empty string when page first loads
		}
		$('#tooltip').hide();
		
		$('input[name=url]').val(url);
		$('#results').empty().append(
			//'<img src="loading.gif">'
			'<em>Loading...</em>'
		).addClass('loading');
		$('#refinements').empty();
		
		$.ajax({
			url: url, 
			success: function(domOrJson) {
				var is_xml = false;
				if (typeof domOrJson.nodeType != 'undefined') {
					// It's an XML DOM
					is_xml = true;
					var root = $(domOrJson).find('*:first');
					var ol = $(document.createElement('ol'));
					ol.addClass('root');
					openplatform.buildListFromXml(ol[0], root[0]);
					$('#results').removeClass('loading').empty().append(ol);
				} else {
					// It should be a JSON object
					if (typeof domOrJson == 'string') {
						domOrJson = eval('(' + domOrJson+ ')');
					}
					$('#results').empty().append(
						openplatform.htmlFromJson(domOrJson)
					).removeClass('loading');
				}
				
				hookupLinks();
			},
			error: function(xhr, status) {
				$('#results').html(
					'An error occurred: "' + status + 
					'". <a href="' + url + '">view API response</a>'
				);
			}
		});
	}
	
	function formatUrl(url, format) {
		if (/format=\w+/.exec(url)) {
			url = url.replace(/format=\w+/, 'format=' + format);
		} else {
			// Add format parameter
			if (/\?/.exec(url)) {
				url = url + '&format=' + format;
			} else {
				url = url + '?format=' + format;
			}
		}
		return url;
	}
	
	function hookupLinks() {
		// Hook up links to the API to call Ajax instead
		$('a[href*=/openout/]').not(
			'.no-modify'
		).unbind('.explorer').bind('click.explorer', function(ev) {
			ev.preventDefault();
			$.history.load(this.getAttribute('href'));
			return false;
		}).attr(
			'title', 'Click to open in the API Explorer'
		).not('.hastooltip').tooltip({
			showURL: false
		}).addClass('hastooltip');
		
		// Links to images should show that image in the tooltip
		$('a[href$=.jpg],a[href$=.gif],a[href$=.png]').not(
			'.hastooltip'
		).tooltip({
			bodyHandler: function() {
				return $("<img/>").attr("src", this.href);
			},
			showURL: false,
			extraClass: 'tooltip-img'
		}).addClass('hastooltip');
	}
	hookupLinks();
});
