var count = 0;
$(document).ready(function(){
	$('#addProxyButton').click(function(){
		//as long the field already exists, keep counting
		count = 0;
		while( $("#item"+count).length > 0){
			count += 1;
		}
		$('#itemhidden.proxy_item').clone().attr('id',"item"+count).attr('style','').appendTo($('.proxy_list'));
		$("#item"+count+">div>div>div>select").each( function(){
			currentid = $(this).attr('id');
			$(this).attr('id',currentid+''+count);
			currentname = $(this).attr('name');
			$(this).attr('name',currentname+''+count);
		});
		$("#tagfieldcount").val(""+(count+1));
		$("#item"+count+">div>div>div>select").chosen({no_results_text: "No results matched",width: "100%%"});
		count += 1;
	});
	
	count = 0;
	while( $("#item"+count).length > 0){
		count += 1;
	}
	if(count==0){
		$('#addProxyButton').click();
	}
	
});