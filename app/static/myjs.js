/**
 * Created by zhaijy on 2017/9/18.
 */
//实现方式一(hover)
$(function() {

   //将除了第一div隐藏
   $('.module:not(:first)').hide();

   $('.title-item').hover(function(e){
       $('.title-item').removeClass('select');//清除所有的select样式
       $(this).addClass('select');//当前加上select样式
       //console.log($(this).index());
       $('.module').hide();
       $('.module').eq($(this).index()).show();//显示对应div
   },function(){

   });
});