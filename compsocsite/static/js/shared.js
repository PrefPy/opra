jQuery(document).ready(function(){
    if ($('#right-sortable li').length!=0){
        $('#submitbutton').attr("disabled", "disabled");
        $('#submitbutton').addClass('btn-disabled');
    }
    
    $('#right-sortable').on('click','li',function(){
        $(this).appendTo($('#left-sortable'));
        if ($('#right-sortable li').length == 0){
            $('#submitbutton').removeAttr("disabled");
            $('#submitbutton').removeClass('btn-disabled');
        }
    });
    
    $('#moveAll').click(function(e){
        e.preventDefault();
        $('#right-sortable li').appendTo($('#left-sortable'));
        $('#submitbutton').removeAttr("disabled");
        $('#submitbutton').removeClass('btn-disabled');
    });
    
    $('#clearbutton').click(function(e){
        e.preventDefault();
        $('#left-sortable li').appendTo($('#right-sortable'));
        $('#left-sortable').empty();
        $('#submitbutton').attr("disabled", "disabled");
         $('#submitbutton').addClass('btn-disabled');
    });
    
    $('#submitbutton').click(function(e){
        var prefcolumn = $('#left-sortable');
        var order = prefcolumn.sortable("toArray");
        $('#pref_order').val(order.join(","));
        $('#pref_order').submit();
    });
    
    $(function() {
        $("#left-sortable").nestedSortable({
            forcePlaceholderSize: true,
            handle: 'div',
            helper:	'clone',
            items: 'li',
            listType: 'ul',
            opacity: .6,
            placeholder: 'placeholder',
            revert: 250,
            tabSize: 25,
            tolerance: 'pointer',
            toleranceElement: '> div',
            maxLevels: 2,
            isTree: true,
            expandOnHover: 700,
            startCollapsed: false
        });

	   $("#left-sortable, #right-sortable").disableSelection();
    });

});