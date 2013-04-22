var count = 0;
$(document).ready(function(){
	$('#addProxyButton').click(function(){
		//as long the field already exists, keep counting
		while( $("#item"+count).length > 0){
			count += 1;
		}
		$('#itemhidden.proxy_item').clone().attr('id',"item"+count).attr('style','').appendTo($('.proxy_list'));
		$("#item"+count+">select").each( function(){
			currentid = $(this).attr('id');
			$(this).attr('id',currentid+''+count);
			currentname = $(this).attr('name');
			$(this).attr('name',currentname+''+count);
		});
		$("#tagfieldcount").val(""+(count+1));
		$("#item"+count+">select").chosen({no_results_text: "No results matched"});
		count += 1;
	});
});