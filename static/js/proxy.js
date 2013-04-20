var count = 0;
$(document).ready(function(){
	$('#addProxyButton').click(function(){
		count += 1;
		$('#0.proxy_item').clone().attr('id',count).attr('style','').appendTo($('.proxy_list'));
		$("#"+count+">select").each( function(){
			currentid = $(this).attr('id');
			$(this).attr('id',currentid+''+count);
		});
		$("#"+count+">select").chosen({no_results_text: "No results matched"});
	});
});