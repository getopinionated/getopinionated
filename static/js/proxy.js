var count = 0;
$(document).ready(function(){
	$('#addProxyButton').click(function(){
		count += 1;
		$('#proxy_list').append('<strong>Link #' + count + '</strong>'+ '<input id="field_' + count + '" name="fields[]' + '" type="text" />' );
	});
});