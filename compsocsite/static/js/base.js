$(document).ready(function() {
	$('.multiple-select').select2();
});

//tooltip
$(document).ready(function(){
	$('[data-toggle="tooltip"]').tooltip();
});

// Scrolls to the selected menu item on the page
$(function() {
	$("a[href*='#']:not([href='#'])").click(function() {
		if (location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') || location.hostname == this.hostname) {
			var target = $(this.hash);
			target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
			if (target.length) { return true; }
			return false;
		}
	});
});


//#to-top button appears after scrolling
var fixed = false;
$(document).scroll(function() {
	if ($(this).scrollTop() > 250) {
		if (!fixed) {
			fixed = true;
			// $('#to-top').css({position:'fixed', display:'block'});
			$('#to-top').show("slow", function() {
				$('#to-top').css({
					position: 'fixed',
					display: 'block'
				});
			});
		}
    } else {
		if (fixed) {
			fixed = false;
			$('#to-top').hide("slow", function() {
				$('#to-top').css({
					display: 'none'
				});
			});
		}
	}
});

$('#username').on('keypress', function (event) {
	var regex = new RegExp("^[a-zA-Z0-9]+$");
	var key = String.fromCharCode(!event.charCode ? event.which : event.charCode);
	alert(key);
	if (!regex.test(key)) {
		event.preventDefault();
		return false;
	}
});


var QueryString = function () {
	// This function is anonymous, is executed immediately and
	// the return value is assigned to QueryString!

	var query_string = {};
	var query = window.location.search.substring(1);
	var vars = query.split("&");
	for (var i=0;i<vars.length;i++) {
		var pair = vars[i].split("=");
		// If first entry with this name
		if (typeof query_string[pair[0]] === "undefined") {
			query_string[pair[0]] = decodeURIComponent(pair[1]);
		// If second entry with this name
		} else if (typeof query_string[pair[0]] === "string") {
			var arr = [ query_string[pair[0]],decodeURIComponent(pair[1]) ];
			query_string[pair[0]] = arr;
		// If third or later entry with this name
		} else {
			query_string[pair[0]].push(decodeURIComponent(pair[1]));
		}
	}
	return query_string;
}();


if (typeof(QueryString["name"]) != "undefined"){
	$('#username').val(QueryString["name"]);
	$('#password').focus();
}
else{
	$('#username').focus();
}

