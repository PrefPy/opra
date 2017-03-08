//  Helper JavaScript created for the voting page (detail.html)
var record = "";
var submissionURL = "";
var order1 = "";
var order2 = "";
var flavor = "";
var startTime = 0;
var allowTies = true;
var commentTime = "";
var method = 1; //1 is twoCol, 2 is oneCol, 3 is Slider

function orderCol(num){
	var arr;
	if(num == 1){ arr = [$('#left-sortable'), $('#right-sortable')]; }
	else if(num == 2){ arr = [$('#one-sortable')]; }
	var order = [];
	$.each(arr, function( index, value ){
		value.children().each(function( index ){
			if( $( this ).children().size() > 0 ){
				var inner = [];
				$( this ).children().each(function( index ){
					inner.push($( this ).attr('type'));
				});
				order.push(inner);
			}
		});
	});
	return order;
}

function orderSlideStar(str){
	var arr = [];
	var values = [];
	$('.' + str).each(function(i, obj){
		if(str == 'slide'){ var score = $( this ).slider("option", "value"); }
		else if(str == 'star'){ var score = parseInt($( this ).rateYo("option", "rating")); }
		else{ return false; }
		var type = $( this ).attr('type')
		var bool = 0;
		$.each(values, function( index, value ){
			if(value < score){
				values.splice(index, 0, score);
				arr.splice(index, 0, [type]);
				bool = 1;
				return false;
			}else if(value == score){
				arr[index].push(type);
				bool = 1;
				return false;
			}
		});
		if(bool == 0){ values.push(score); arr.push([type]); }
	});
	return arr;
}

function twoColSort( order ){
	var html = "<ul class=\"choice1 empty\"></ul>";
	$.each(order, function(index, value){
		html += "<ul class=\"choice1\"><div class=\"tier\">" + index.toString() + "</div>";
		$.each(value, function(i, v){
			html += "<li class=\"li_item\" id=\"" + $(".li_item[type='" + v.toString() + "']").attr('id') + "\" type=" + v.toString() + ">";
			html += $(".li_item[type='" + v.toString() + "']").html();
			html += "</li>";
		});
		html += "</ul><ul class=\"choice1 empty\"></ul>";
	});
	$('#left-sortable').html(html);
	$('#right-sortable').html("");
}

function oneColSort( order ){
	var html = "<ul class=\"choice2 empty\"></ul>";
	$.each(order, function(index, value){
		html += "<ul class=\"choice2\"><div class=\"tier\">" + index.toString() + "</div>";
		$.each(value, function(i, v){
			html += "<li class=\"one_li_item\" id=\"" + $(".one_li_item[type='" + v.toString() + "']").attr('id') + "\" type=" + v.toString() + ">";
			html += $(".one_li_item[type='" + v.toString() + "']").html();
			html += "</li>";
		});
		html += "</ul><ul class=\"choice2 empty\"></ul>";
	});
	$('#one-sortable').html(html);
}

function sliderSort( order ){
	$.each(order, function(index, value){
		$.each(value, function(i, v){
			$(".slide[type='" + v.toString() + "']").slider("value", Math.round(100 - (100 * index / order.length)));
			$("#score" + $(".slide[type='" + v.toString() + "']").attr("id")).text(Math.round(100 - (100 * index / order.length)));
		});
	});
}

function starSort( order ){
	$.each(order, function(index, value){
		$.each(value, function(i, v){
			$(".star[type='" + v.toString() + "']").rateYo("option", "rating", Math.round(10 - (10 * index / order.length)) / 2);
		});
	});
}

function changeMethod (value){
	var order;
	if(method == 1){ 
		$("#twoCol").hide();
		order = orderCol(method);
	}else if(method == 2){
		$("#oneCol").hide();
		order = orderCol(method);
	}
	else if(method == 3){
		$("#slider").hide();
		order = orderSlideStar('slide');
	}
	else if(method == 4){
		$("#star").hide();
		order = orderSlideStar('star');
	}
	console.log(order.length);
	method = parseInt(value.value);
	if(method == 1){ $("#twoCol").show(); twoColSort(order); }
	else if(method == 2){ $("#oneCol").show(); oneColSort(order); }
	else if(method == 3){ $("#slider").show(); sliderSort(order); }
	else if(method == 4){ $("#star").show(); starSort(order); }

	VoteUtil.checkStyle();
};

function recordCommentTime(){
	if(commentTime == ""){
		var d = Date.now() - startTime  ;
		commentTime += d;
	}
	
}
// the VoteUtil object contains all the utility functions for the voting UI
var VoteUtil = (function () {
	// returns true if the user is on a mobile device, else returns false
	function isMobileAgent () {
		return /Android|webOS|iPhone|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
	}
	
	// clears all items from the left side and returns the right side to its default state
	function clearAll () {
		if(method == 1){
			// move the left items over to the right side
			$("#left-sortable").children().each(function(index){
				if($(this).children().size() > 0){
					var tier = 1;
					$(this).children().each(function(index){
						var temp = $("#right-sortable" ).html();
						$("#right-sortable" ).html( temp + "<ul class=\"choice2 empty\"></ul>"
							+ "<div class=\"tier\">" + tier + "</div>"
							+ "<ul class=\"choice2\" onclick =\"VoteUtil.moveToPref(this)\">" + $(this)[0].outerHTML + "</ul>" );
					});
				}
			});
			
			// clear the items from the left side
			$( '#left-sortable' ).html("");
			
			checkStyle();
			disableSubmission();
			// add the clear action to the record
			var d = Date.now() - startTime;
			record += d + "||";
			$( "#right-sortable" ).children().each(function( index ) {
				if($(this).children().size()>0){
					record += $(this).children().first().attr("id") + "||"
				}
			});
			record += ";;;";
		}
	}
	
	function insideEach(t, id, tier){
		if( $( t ).children().size() < 1 ){
			$( t ).remove();
		}else{
			$( t ).attr("id", id.toString());
			id += 1;
			$( t ).before("<ul class=\"choice1 empty\" id=\"" + id.toString() + "\"></ul>");
			if( $( t ).attr('class').indexOf('empty')>-1 ){ $( t ).removeClass('empty').addClass('choice1'); }
			if( $( t ).children().size() < 2 || isMobileAgent() ){
				$( t ).children().css( "width", "93%" );
			}else{
				$( t ).children().css( "width", "45%" ).css("display","inline-block").css("vertical-align","top");
			}
			$( t ).before("<div class=\"tier\" style=\"padding-top:" + ($( this )[0].scrollHeight / 3).toString() + "px;\">" + tier + "</div>");
			$( t ).children().each(function(index){$(this).attr("alt",tier.toString()); });
			tier += 1;
			id += 1;
		}
		return [id, tier]
	}
	
	function checkStyle () {
		if(method < 3){
			newItem = "<ul class=\"choice1 empty\"></ul>";
			var tier = 1;
			var id = 0;
			if(method == 1){ submission = $("#left-sortable"); }
			else{ submission = $("#one-sortable"); }
			$( ".tier" ).each(function( index ) {
				$( this ).remove();
			});
			submission.children().each(function( index ) {
				arr = insideEach(this, id, tier);
				id = arr[0];
				tier = arr[1];
				if($(this).children().size() >=1 ){
					$(this).attr("class","choice1");
				}
			});
			submission.children().last().after("<ul class=\"choice1 empty\" id=\"" + id.toString() + "\"></ul>");
			if(method == 1){
				tier = 1;
				$( "#right-sortable" ).children().each(function( index ) {
					arr = insideEach(this, id, tier);
					id = arr[0];
					tier = arr[1];
				});
				if($( "#right-sortable" ).children().size() > 0){
					$( "#right-sortable" ).children().last().after("<ul class=\"choice1 empty\" id=\"" + id.toString() + "\"></ul>");
				}
				if( $( "#right-sortable" ).children().size() == 0 ){ enableSubmission(); }
			}
		}
	}
	
	// submits the current left side preferences	
	function submitPref() {
		if(method != 1){
			var order_list;
			if(method == 2){ order_list = orderCol(method); }
			else if(method == 3){ order_list = orderSlideStar('slide'); }
			else if(method == 4){ order_list = orderSlideStar('star'); }
			else{ location.reload(); }
			twoColSort(order_list);
		}
		var prefcolumn = $('#left-sortable');
		var order = "";
		var d = Date.now() - startTime;
		record += "S" + d;
		prefcolumn.children().each(function( index ){
			if( $( this ).children().size() > 0 ){
				$( this ).children().each(function( index ){
					if($( this ).attr('id')){
						order += $( this ).attr('id');
					order += ";;";
          }
				});
				order += "|;;";
			}
		});
		$('.pref_order').each(function(){
			$(this).val(order);
		});
		
		$.ajax({
			url: submissionURL,
			type: "POST",
			data: {'data': record, 'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(), 'order1':order1,'order2':order2,'final':order,'device':flavor,'commentTime':commentTime},
			success: function(){}
		});
		document.getElementById('submitbutton').style.visibility = "hidden";
		document.getElementById('submitting').style.visibility = "visible";
		$('#pref_order').submit();
	};
	
	// moves preference item obj from the right side to the bottom of the left side
	function moveToPref(obj) {
		var time = 100
		var prefcolumn = $('#left-sortable');
		var currentli = $(obj);
		var tier = currentli.children().first().attr("alt");
		var d = Date.now() - startTime;
		var item = currentli.children().first().attr("id");
		console.log(obj.id);
		prefcolumn.append(currentli);
		record += d+ "::clickFrom::" + item + "::"+ tier+";;";
		VoteUtil.checkStyle();
		tier = currentli.children().first().attr("alt");
		if ($('#right-sortable').children().size() == 0) { enableSubmission(); }
		$('#left-sortable').children().each(function(){
			$(this).removeAttr('onclick');
		});
		d = Date.now() - startTime;
		record += d+ "::clickTo::" + item + "::"+ tier+";;;";
	};
	
	// moves all items from the right side to the bottom of the left, preserving order
	function moveAll() {
		$( '#left-sortable' ).html( $( '#left-sortable' ).html() + $( '#right-sortable' ).html() );
		$( '#right-sortable' ).html("");
		VoteUtil.checkStyle();
		enableSubmission();
		$('#left-sortable li').each(function(){
			$(this).removeAttr('onclick');
		});
		var d = Date.now() - startTime;
		record += d + ";;;";
		
	};
	
	// enables the submit button
	function enableSubmission() {
		if( VoteUtil.isMobileAgent() ){
			$("#submitbutton").css("display", "inline");
		}else{
			document.getElementById('submitbutton').disabled = false;
		}
	}
	
	function disableSubmission(){
		if( VoteUtil.isMobileAgent() ){
			$("#submitbutton").css("display", "none");
		}else{
			document.getElementById('submitbutton').disabled = true;
		}
	}
	// returns the public members of the VoteUtil class
	return {
		isMobileAgent: isMobileAgent,
		clearAll: clearAll,
		checkStyle: checkStyle,
		submitPref: submitPref,
		moveToPref: moveToPref,
		moveAll: moveAll	
	}
	
})()




$( document ).ready(function() {
	!function(a){function f(a,b){if(!(a.originalEvent.touches.length>1)){a.preventDefault();var c=a.originalEvent.changedTouches[0],d=document.createEvent("MouseEvents");d.initMouseEvent(b,!0,!0,window,1,c.screenX,c.screenY,c.clientX,c.clientY,!1,!1,!1,!1,0,null),a.target.dispatchEvent(d)}}if(a.support.touch="ontouchend"in document,a.support.touch){var e,b=a.ui.mouse.prototype,c=b._mouseInit,d=b._mouseDestroy;b._touchStart=function(a){var b=this;!e&&b._mouseCapture(a.originalEvent.changedTouches[0])&&(e=!0,b._touchMoved=!1,f(a,"mouseover"),f(a,"mousemove"),f(a,"mousedown"))},b._touchMove=function(a){e&&(this._touchMoved=!0,f(a,"mousemove"))},b._touchEnd=function(a){e&&(f(a,"mouseup"),f(a,"mouseout"),this._touchMoved||f(a,"click"),e=!1)},b._mouseInit=function(){var b=this;b.element.bind({touchstart:a.proxy(b,"_touchStart"),touchmove:a.proxy(b,"_touchMove"),touchend:a.proxy(b,"_touchEnd")}),c.call(b)},b._mouseDestroy=function(){var b=this;b.element.unbind({touchstart:a.proxy(b,"_touchStart"),touchmove:a.proxy(b,"_touchMove"),touchend:a.proxy(b,"_touchEnd")}),d.call(b)}}}(jQuery);

	// Google Analytics
	// -----------------------------------------------------------------------
	//	 (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
	//	 (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
	//	 m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
	//	 })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');

	//	 ga('create', 'UA-81006265-1', 'none');
	//  //ga('create', 'UA-81006265-1', 'none','DetailTracker');
	//	 ga('send', 'pageview');
	//  ga('send', 'event', 'Button', 'click', 'left-sortable');
	//  //ga('DetailTracker.send', 'pageview');
	// ga(function(tracker) {
	//	 // Logs the tracker created above to the console.
	//	 console.log(tracker);
	// });
	//		 var form=document.getElementById('left-sortable');
	//		 form.addEventListener('submit', function(event) {

	//	 // Prevents the browser from submiting the form
	//	 // and thus unloading the current page.
	//	 event.preventDefault();

	//	 // Sends the event to Google Analytics and
	//	 // resubmits the form once the hit is done.
	//	 ga('send', 'event', 'Left Form', 'submit', {
	//		 hitCallback: function() {
	//			 form.submit();
	//		 }
	//	 });
	// });
	//	 // -----------------------------------------------------------------------
	//	 // Google Tag Manager
	// (function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
	// new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
	// j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
	// '//www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
	// })(window,document,'script','dataLayer','GTM-59SLDM');
	// -----------------------------------------------------------------------

	/*
	var wholeHeight1 = $('#left-sortable')[0].scrollHeight;
	var wholeHeight2 = $('#right-sortable')[0].scrollHeight;
	if (wholeHeight1 > wholeHeight2) {
		$('#right-sortable').css("height", wholeHeight1);
	} else {
		$('#left-sortable').css("height", wholeHeight2);
	}
	*/
	// $('#left-sortable').sortable('refresh');
	// $('#right-sortable').sortable('refresh');
		  
	$('.hide1').mouseover(function(){
		$('.ept',this).show();
	});
	VoteUtil.checkStyle();
	
	function enableSubmission() {
		$('#submitbutton').css("display", "inline");
	}
	
	
	var oldList, newList, item;
	
	window.setInterval(function(){
		// $("#left-sortable").sortable({
		//	 start: function(event, ui){
		//		 $( ".empty" ).each(function( index ) { $( this ).remove(); });
		//		 $( ".tier" ).each(function( index ) { $( this ).css("display", "none"); }); //get rid of the tier divs
		//	 },
			
		//	 stop: function(event, ui) {
		//		 var len = $(".choice1").length;
		//		 newItem = "<ul class=\"choice1 empty\"></ul>";
		//		 var tier = 1;
		//		 var id = 0;
		//		 $( ".tier" ).each(function( index ) {
		//			 $( this ).remove();
		//		 });
		//		 $( "#left-sortable" ).children().each(function( index ) {
		//			 if( $( this ).children().size() < 1 ){
		//				 $( this ).remove();
		//			 }else{
		//				 $( this ).attr("id", id.toString());
		//				 id += 1;
		//				 $( this ).before("<ul class=\"choice1 empty\" id=\"" + id.toString() + "\"></ul>");
		//				 if( $( this ).attr('class').indexOf('empty')>-1 ){ $( this ).removeClass('empty').addClass('choice1'); }
		//				 if( $( this ).children().size() < 2  
		//					 || ( /Android|webOS|iPhone|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) )){
		//					 $( this ).children().css( "width", "93%" );
		//				 }else{
		//					 $( this ).children().css( "width", "45%" ).css("display","inline-block").css("vertical-align","top");
		//				 }
		//				 $( this ).before("<div class=\"tier\" style=\"padding-top:" + ($( this )[0].scrollHeight / 3).toString() + "px;\">" + tier + "</div>");
		//				 tier += 1;
		//				 id += 1;
		//			 }
		//		 });
		//		 $( "#left-sortable" ).children().last().after("<ul class=\"choice1 empty\" id=\"" + id.toString() + "\"></ul>");
		//		 $( "#right-sortable" ).children().each(function( index ) {
		//			 if( $( this ).children().size() < 1 ){
		//				 $( this ).remove();
		//			 }else{
		//				 $( this ).attr("id", id.toString());
		//				 id += 1;
		//				 $( this ).before("<ul class=\"choice1 empty\" id=\"" + id.toString() + "\"></ul>");
		//				 if( $( this ).attr('class').indexOf('empty')>-1 ){ $( this ).removeClass('empty').addClass('choice1'); }
		//				 if( $( this ).children().size() < 2 
		//					 || ( /Android|webOS|iPhone|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) )){
		//					 $( this ).children().css( "width", "93%" );
		//				 }else{
		//					 $( this ).children().css( "width", "45%" ).css("display","inline-block").css("vertical-align","top");
		//				 }
		//				 $( this ).before("<div class=\"tier\" style=\"padding-top:" + ($( this )[0].scrollHeight / 3).toString() + "px;\">" + tier + "</div>");
		//				 tier += 1;
		//				 id += 1;
		//			 }
		//		 });
		//		 if($( "#right-sortable" ).children().size() > 0){
		//			 $( "#right-sortable" ).children().last().after("<ul class=\"choice1 empty\" id=\"" + id.toString() + "\"></ul>");
		//		 }
		//		 if( $( "#right-sortable" ).children().size() == 0 ){ document.getElementById('submitbutton').disabled = false; }
		//	 },

		//	 change: function(event, ui) {  
		//		 if(ui.sender){
					
		//			 //variables
		//			 newList = ui.placeholder.parent(); //the list the item is hovering over
		//			 var newListId = parseInt($( newList ).attr("id")); //the id of the list
		//			 var oldListId = parseInt($( oldList ).attr("id")); //the id of the old list
		//			 var listId;
		//			 var prevEmpty = false;
					
					
		//			 newItem = "<ul class=\"choice1 empty line\"></ul>";
		//			 var tier = 1;

		//			 $( ".tier" ).each(function( index ) { $( this ).remove(); }); //get rid of the tier divs
		//			 $( ".line" ).each(function( index ) { $( this ).remove(); }); //get rid of placeholder uls

		//			 $( "ul.choice1" ).each(function(index){
		//				 console.log("this");
		//				 if($( this ).children().size() != 0){
		//					 console.log("hi");
		//					 $( this ).before(newItem);
		//				 }
		//			 });
					
		//			 ui.placeholder.css("width", "93%");
		//			 ui.placeholder.height(ui.item.height());
		//		 }
		//	 },
		//	 placeholder: "ui-state-highlight",
		//	 items: "ul:not(.empty)"
		// });
		
		//$("ul.choice1").sortable({
		
		if(method == 1){
			var sortableSelector = 'ul#left-sortable';
			var submission = $("#left-sortable");
		}else if(method == 2){
			var sortableSelector = 'ul#one-sortable';
			var submission = $("#one-sortable");
		}
		
		if (allowTies)
			sortableSelector = 'ul.choice1'
		else
			$('ul.choice1.empty').remove()
		
		$(sortableSelector).sortable({
		   
			start: function(event, ui) {
				ui.placeholder.height(ui.item.height());
				item = ui.item;
				
				if ( item.parent().children().size() < 3 || VoteUtil.isMobileAgent() ){
					ui.placeholder.css("width", "93%");
					ui.item.width(ui.placeholder.width());
				} else if (allowTies) {
					ui.placeholder.css("width", "45%").css("display","inline-block").css("vertical-align","top");
					ui.item.width(ui.placeholder.width());
				};
				newList = oldList = oL = ui.item.parent();
				var d = Date.now() - startTime;
				record += d+ "::start::" + item.attr("id") + "::"+ item.attr("alt")+";;";
				/*
				$.ajax({
					url: "{% url 'polls:record' question.id%}",
					type: "POST",
					data: {'time': Data.now(), 'status':"start",'item': item.attr("id"), 'position': item.parent().children().first().html(), 'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()},
					success: function(){}
				});
				*/
				
				if (!allowTies) {
					ui.placeholder.css("width", "84%");
					ui.placeholder.css("margin-left", "35px");
					ui.item.width(ui.placeholder.width());
				}
			},
			
			stop: function(event, ui) {
				var len = $(".choice1").length;
				newItem = "<ul class=\"choice1 empty\"></ul>";
				var tier = 1;
				var id = 0;
				$( ".tier" ).each(function( index ) {
					$( this ).remove();
				});
				submission.children().each(function( index ) {
					if( $( this ).children().size() < 1 ){
						$( this ).remove();
					}else{
						$( this ).attr("id", id.toString());
						$( this ).children().each(function( index ) {
							$( this ).attr("alt", tier.toString());
						});
						id += 1;
						if (allowTies)
							$( this ).before("<ul class=\"choice1 empty\" id=\"" + id.toString() + "\"></ul>");
						
						if( $( this ).attr('class').indexOf('empty')>-1 ){ $( this ).removeClass('empty').addClass('choice1'); }
						if( $( this ).children().size() < 2 || VoteUtil.isMobileAgent() ){
							$( this ).children().css( "width", "93%" );
						}else{
							$( this ).children().css( "width", "45%" ).css("display","inline-block").css("vertical-align","top");
						}
						$( this ).before("<div class=\"tier\" style=\"padding-top:" + ($( this )[0].scrollHeight / 3).toString() + "px;\">" + tier + "</div>");
						tier += 1;
						id += 1;
					}
				});
				if (allowTies)
					submission.children().last().after("<ul class=\"choice1 empty\" id=\"" + id.toString() + "\"></ul>");
					if(method == 1){
						$( "#right-sortable" ).children().each(function( index ) {
							if( $( this ).children().size() < 1 ){
								$( this ).remove();
							}else{
								$( this ).attr("id", id.toString());
								id += 1;
								$( this ).before("<ul class=\"choice1 empty\" id=\"" + id.toString() + "\"></ul>");
								if( $( this ).attr('class').indexOf('empty')>-1 ){ $( this ).removeClass('empty').addClass('choice1'); }
								if( $( this ).children().size() < 2 || VoteUtil.isMobileAgent() ){
									$( this ).children().css( "width", "93%" );
								}else{
									$( this ).children().css( "width", "45%" ).css("display","inline-block").css("vertical-align","top");
								}
								$( this ).before("<div class=\"tier\" style=\"padding-top:" + ($( this )[0].scrollHeight / 3).toString() + "px;\">" + tier + "</div>");
								tier += 1;
								id += 1;
							}
						});
						if($( "#right-sortable" ).children().size() > 0){
							$( "#right-sortable" ).children().last().after("<ul class=\"choice1 empty\" id=\"" + id.toString() + "\"></ul>");
						}
						if( $( "#right-sortable" ).children().size() == 0 ){ document.getElementById('submitbutton').disabled = false; }
					}
				var t = parseInt(item.attr("alt"));
				var count = 0;
				var itemsSameTier = "";
				submission.children().each(function(index){
					if($(this).children().size()>=1){
						count++;
					}
					if(count == t){
						$(this).children().each(function(index){
							itemsSameTier += $(this).attr("id") + "||";
						});
						return false;
					}
				});
				var d = Date.now() - startTime;
				record += d+ "::stop::" + item.attr("id") + "::"+ item.attr("alt") + "||" + itemsSameTier +";;;";
			},

			change: function(event, ui) {
				if(ui.sender || !allowTies){
						
					//variables
					newList = ui.placeholder.parent(); //the list the item is hovering over
					var newListId = parseInt($( newList ).attr("id")); //the id of the list
					var oldListId = parseInt($( oldList ).attr("id")); //the id of the old list
					var listId;
					var prevEmpty = false;
					
					newItem = "<ul class=\"choice1 empty line\"></ul>";
					var tier = 1;

					$( ".tier" ).each(function( index ) { $( this ).remove(); }); //get rid of the tier divs
					$( ".line" ).each(function( index ) { $( this ).remove(); }); //get rid of placeholder uls

					//go through each list from the top
			 
					$( ".choice1" ).each(function( index ) {
						listId = parseInt($( this ).attr("id"));
						if( $( this ).children().size() < 1 ){
							// if this list does not have contain any alternative, then mark it to be "empty"
							$( this ).addClass('empty');
							// if there are two empty lists next to each other, then remove the current one	 
							if(prevEmpty){
								$( this ).remove();
							}else{
								prevEmpty = true;
							}	 
						}else if((listId == oldListId && listId != newListId
							&& $( oldList ).children().size() == 1)){
							$( this ).css("height", "0");
							prevEmpty = true;
						}else if($( this ).height()>0){
							
							//current list contains at least one alternative but is marked "empty"
							if( $( this ).attr('class').indexOf('empty')>-1 ){
								$( this ).removeClass('empty');
								//should remove empty and add new "empty" lists around it
								$( this ).after(newItem);							
								//if($( oldList ).children().size() != 1 || newListID != oldListId+3)
								
								if (index >0){
									//previoius = $( ".choice1" )[index-1].size();
									previoussize = $($( '#left-sortable ul' )[index-1]).size();
									//alert(index+" "+previous);
									//if (previoussize>1)
									{
										
									$( this ).before(newItem);
								}
								}
								else{
									$( this ).before(newItem);
								}
								
									
							}
							if( $( this ).children().size() < 2 || VoteUtil.isMobileAgent() || ! allowTies){
								$( this ).children().css( "width", "93%" );
							}else{
								$( this ).children().css( "width", "45%" ).css("display","inline-block").css("vertical-align","top");
							}
							//if (allowTies && left)
							//if (allowTies || !$(this).hasClass("ui-sortable-helper")) {
							if (allowTies)
								$( this ).before("<div class=\"tier\" style=\"padding-top:" + ($( this )[0].scrollHeight / 3).toString() + "px;\">" + tier + "</div>");
								tier += 1;
							//}
							prevEmpty = false;
						}
					}
					
					);
					
					if (!allowTies)
						$('#left-sortable > ul:not(.ui-sortable-helper)').each(function (i) {
							$( this ).before("<div class=\"tier\" style=\"padding-top:" + ($( this )[0].scrollHeight / 3).toString() + "px;\">" + (i + 1) + "</div>");
						})
					
					//second scan to remove the double "empty" bars
					prevEmpty = false;
					
					$( ".choice1" ).each(function( index ) {
						if( $( this ).children().size() < 1 ){
							// if this list does not have contain any alternative, then mark it to be "empty"
							$( this ).addClass('empty');
							// if there are two empty lists next to each other, then remove the current one	 
							if(prevEmpty){
								$( this ).remove();
							}else{
								prevEmpty = true;
							}	 
						}
						else if($( this ).height()>0){
							prevEmpty = false;
						}
							
					}
					);
					
					if( $(newList).children().size() > 1 && !VoteUtil.isMobileAgent() && allowTies){
						ui.placeholder.css("width", "45%").css("display","inline-block").css("vertical-align","top");
						ui.item.width(ui.placeholder.width());
					}else{
						ui.placeholder.css("width", "93%");
						ui.item.width(ui.placeholder.width());
					}
					
					if (!allowTies) {
						ui.placeholder.css("width", "84%");
						ui.placeholder.css("margin-left", "35px");
						ui.item.width(ui.placeholder.width());
					}
					
				}
				
			},
			placeholder: "ui-state-highlight",
			connectWith: "ul.choice1, ul.empty",
		}).disableSelection();
	}, 1000);
	
	//if the user updates existing preferences, the submit button should be shown
	if ($('#right-sortable li').length == 0) {
		enableSubmission();
	}
	VoteUtil.checkStyle();
	$(".slide").each(function(){
		$(this).slider({
			step: 1,
			slide: function( event, ui ) {
				$("#score" + this.id).text(ui.value);
			}
		});
	});
	$(".star").each(function(){
		$(this).rateYo({
			halfStar: true
		});
	});
	var t = 1
	$(".li_item").each(function(){
		$(this).attr({type:t.toString()});
		t += 1;
	});
});