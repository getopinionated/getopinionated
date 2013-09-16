/**
 * String.format function
 *
 * see: http://stackoverflow.com/questions/4974238/javascript-equivalent-of-pythons-format-function
 * usage: "The lazy {} {} over the {}".format("dog", "jumped", "foobar");
 *          outputs:
 *        "The lazy dog jumped over the foobar"
 */
String.prototype.format = function () {
  var i = 0, args = arguments;
  return this.replace(/{(.*?)}/g, function (match, tagInner) {
    replacement = typeof args[i] != 'undefined' ? args[i++] : '';
    if(tagInner == "") {
        return replacement;
    } else {
        var match = tagInner.match(/^:.(\d+)f$/);
        if(match) {
            precision = parseInt(match[1]);
            return parseFloat(replacement).toFixed(precision);
        } else {
            return replacement
        }
    }
  });
};

/*** apply popovers to all elements with popovertitle as attr ***/
$( document ).ready(function () {
    $('.custom-popover').each(function(){
        $(this).popover({
            animation: true,
            html: false,
            placement: "bottom",
            trigger: "hover",
            content: $(this).attr('popovertitle')
        });
    });
});