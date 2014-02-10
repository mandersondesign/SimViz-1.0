/* [ ---- Gebo Admin Panel - buttons ---- ] */

	$(document).ready(function() {
		$('#fat-btn').click(function () {
			var btn = $(this);
			btn.button('loading');
			setTimeout(function () {
				btn.button('reset')
			}, 3000)
		});
		
	});
