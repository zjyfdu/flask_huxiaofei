/**
 * Created by zhaijy on 2017/9/18.
 */
//实现方式一(hover)
$(function() {

   //将除了第一div隐藏
   $('.module:not(:first)').hide();

   $('ul.nav-tabs>li').click(function(){
       $('ul.nav-tabs>li').removeClass('active');//清除所有的select样式
       $(this).addClass('active');//当前加上select样式
       $('.module').hide();
       $('.module').eq($(this).index()).show();//显示对应div
   });
});