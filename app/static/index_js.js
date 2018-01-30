/**
 * Created by zhaijy on 2018/1/30.
 */

    $(document).ready(function(){
        var the_width=Number($(window).width());
        if(the_width<970){
            var cehua_body=$(".cehua_body").html();
            var cehua_title=$(".cehua_title").html();
            $(".cehua_title").html(cehua_body);
            $(".cehua_body").html(cehua_title);
            var xuanchuan_body=$(".xuanchuan_body").html();
            var xuanchuan_title=$(".xuanchuan_title").html();
            $(".xuanchuan_title").html(xuanchuan_body);
            $(".xuanchuan_body").html(xuanchuan_title);
            var shouke_body=$(".shouke_body").html();
            var shouke_title=$(".shouke_title").html();
            $(".shouke_title").html(shouke_body);
            $(".shouke_body").html(shouke_title);
        };
      $(".pas img").addClass("img-responsive");

      $(".hovernav").mouseenter (function(){
        $(this).css({"background":"#B46969","color":"red"});
      });
      $(".hovernav").mouseleave (function(){
        $(this).css("background","#222")

      });
      $(".col-list").mouseenter(function(){
      	$(this).css("box-shadow","0 0 5px 5px #E1E0E0");
      })
      $(".col-list").mouseleave(function(){
      	$(this).css("box-shadow","0 0 5px 5px #EEE");
      });
      $(".data_post").mouseenter(function(){
        $(this).css("box-shadow","5px 5px 20px #C6C5C5");
      });
      $(".data_post").mouseleave(function(){
        $(this).css("box-shadow","0 0 5px 5px #E7E4E4");
      })
      $(".data-post").mouseenter(function(){
        $(this).css("box-shadow","0px 10px 10px #7B7A7A");
      });
      $(".data-post").mouseleave(function(){
        $(this).css("box-shadow","0px 10px 10px #B9B5B5");
      });
    });

