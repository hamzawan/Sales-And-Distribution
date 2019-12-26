$(document).ready(function(){


    function getCookie(c_name)
    {
        if (document.cookie.length > 0)
        {
            c_start = document.cookie.indexOf(c_name + "=");
            if (c_start != -1)
            {
                c_start = c_start + c_name.length + 1;
                c_end = document.cookie.indexOf(";", c_start);
                if (c_end == -1) c_end = document.cookie.length;
                return unescape(document.cookie.substring(c_start,c_end));
            }
        }
        return "";
     }

        var select_user;
          $("#select_user").on('change',function() {
            $('#main_menu').prop('disabled', false);
            $('#sub_menu').prop('disabled', false);
            select_user = this.value;
          });
        $('#main_menu').on('change', function() {
         main_object_id = this.value;
         req =	$.ajax({
          headers: { "X-CSRFToken": getCookie("csrftoken") },
          type: 'POST',
          url : '/roles/new',
          data:{
            'main_object_id':main_object_id ,
          },
          dataType: 'json'
         })
         .done(function done(data) {
           sub_menu = JSON.parse(data.sub_menu)
           $('#sub_menu').empty()
           $('#sub_menu').append($("<option></option>").attr("value",0).text("Select: "));
           for (var i = 0; i < sub_menu.length; i++) {
               $('#sub_menu').append($("<option></option>").attr("value",sub_menu[i].pk).text(sub_menu[i].fields["ObjectTitle"]));
           }
           var menu_name = $('#sub_menu').find(":selected").text();
           $('#menu_name').html(menu_name);
         })
       });
       $('#sub_menu').on('change', function() {
         $('#menu_name').html($(this).find(":selected").text());
         sub_menu_id = this.value;
         req =	$.ajax({
          headers: { "X-CSRFToken": getCookie("csrftoken") },
          type: 'POST',
          url : '/roles/new',
          data:{
            'sub_menu_id':sub_menu_id ,
          },
          dataType: 'json'
         })
         .done(function done(data) {
           $("#new_rights_table").find("tr:gt(0)").remove();
           actions = data.actions;
           console.log("Here",actions)
           var table = $('<table>').addClass('');
           $('#new_rights_table').append( '<tr><th>Action</th><th>Allow</th></tr>');
           for(var i=0; i < actions.length; i++){
               $('#new_rights_table').append( '<tr><td style="display:none;">'+sub_menu_id+'</td><td style="display:none;">'+actions[i][1]+'</td><td>'+actions[i][2]+'</td><td><input type="checkbox" value=""></td></td><td style="display:none;">'+select_user+'</td></tr>');
           }
           $('#new_rights_table').append(table);
         })
       })
       $("#new-roles-submit").on('submit', function(e){
           e.preventDefault();
           var table = $('#new_rights_table');
           var data = [];
           table.find('tr').each(function (i, el){
           if(i != 0 && i != 1)
           {
             var $tds = $(this).find('td');
             var row = {
               'objectID' : "",
               'actionID' : "",
               'actionName' : "",
               'isAllow': "",
               'userID': "",
             };
             $tds.each(function(i, el)
             {
               if (i === 0) {
                   row["objectID"] = ($(this).text());
               }
               else if (i === 1) {
                   row["actionID"] = ($(this).text());
               }
               else if (i === 2) {
                   row["actionName"] = ($(this).text());
               }
               else if (i === 3) {
                 if ($(this).find("input[type=checkbox]").is(':checked')) {
                     row["isAllow"] = 1;
                 }
                 else {
                   row["isAllow"] = 0;
                 }
               }
               else if (i === 4) {
                   row["userID"] = ($(this).text());
               }
             });
             data.push(row);
           }
         });
           req =	$.ajax({
            headers: { "X-CSRFToken": getCookie("csrftoken") },
            type: 'POST',
            url : '/roles/new',
            data:{
              'new_roles':JSON.stringify(data) ,
            },
            dataType: 'json'
           })
           req.done(function(){
             alert("Submitted");
             location.reload();
           });
         })


         var userID = $('#select_user_edit').find(":selected").val();
         $('#main_menu_edit').on('change', function() {
          main_object_id = this.value;
          req =	$.ajax({
           headers: { "X-CSRFToken": getCookie("csrftoken") },
           type: 'POST',
           url : `/roles/edit/${userID}`,
           data:{
             'main_object_id':main_object_id ,
           },
           dataType: 'json'
          })
          .done(function done(data) {
            sub_menu = JSON.parse(data.sub_menu)
            $('#sub_menu_edit').empty()
            $('#sub_menu_edit').append($("<option></option>").attr("value",0).text("Select: "));
            for (var i = 0; i < sub_menu.length; i++) {
                $('#sub_menu_edit').append($("<option></option>").attr("value",sub_menu[i].pk).text(sub_menu[i].fields["ObjectTitle"]));
            }
            var menu_name = $('#sub_menu_edit').find(":selected").text();
            $('#menu_name').html(menu_name);
          })
        });

        $('#sub_menu_edit').on('change', function() {
          $('#menu_name').html($(this).find(":selected").text());
          sub_menu_id = this.value;
          req =	$.ajax({
           headers: { "X-CSRFToken": getCookie("csrftoken") },
           type: 'POST',
           url : `/roles/edit/${userID}`,
           data:{
             'sub_menu_id':sub_menu_id ,
           },
           dataType: 'json'
          })
          .done(function done(data) {
            $("#edit_rights_table").find("tr:gt(0)").remove();
            actions = data.actions;
            var table = $('<table>').addClass('');
            $('#edit_rights_table').append( '<tr><th>Action</th><th>Allow</th></tr>');
            console.log(actions);
            for(var i=0; i < actions.length; i++){
              if (actions[i][2] == 1) {
                var  row = '<tr>'+
                   '<td style="display:none;">'+sub_menu_id+'</td>'+
                   '<td style="display:none;">'+actions[i][0]+'</td>'+
                   '<td>'+actions[i][1]+'</td>'+
                   '<td><input type="checkbox" checked value=""></td>'+
                   '</td><td style="display:none;">'+userID+'</td>'+
                   '</tr>'
              } else {
                var  row = '<tr>'+
                   '<td style="display:none;">'+sub_menu_id+'</td>'+
                   '<td style="display:none;">'+actions[i][0]+'</td>'+
                   '<td>'+actions[i][1]+'</td>'+
                   '<td><input type="checkbox" value=""></td>'+
                   '</td><td style="display:none;">'+userID+'</td>'+
                   '</tr>'
              }
              $('#edit_rights_table').append(row);
            }
          })
        })

        $("#edit-roles-submit").on('submit', function(e){
            e.preventDefault();
            var userID = $('#select_user_edit').find(":selected").val();
            var table = $('#edit_rights_table');
            var data = [];
            table.find('tr').each(function (i, el){
            if(i != 0 && i != 1)
            {
              var $tds = $(this).find('td');
              var row = {
                'objectID' : "",
                'actionID' : "",
                'actionName' : "",
                'isAllow': "",
                'userID': "",
              };
              $tds.each(function(i, el)
              {
                if (i === 0) {
                    row["objectID"] = ($(this).text());
                }
                else if (i === 1) {
                    row["actionID"] = ($(this).text());
                }
                else if (i === 2) {
                    row["actionName"] = ($(this).text());
                }
                else if (i === 3) {
                  if ($(this).find("input[type=checkbox]").is(':checked')) {
                      row["isAllow"] = 1;
                  }
                  else {
                    row["isAllow"] = 0;
                  }
                }
                else if (i === 4) {
                    row["userID"] = ($(this).text());
                }
              });
              data.push(row);
            }
          });
            req =	$.ajax({
             headers: { "X-CSRFToken": getCookie("csrftoken") },
             type: 'POST',
             url : `/roles/edit/${userID}`,
             data:{
               'edit_roles':JSON.stringify(data) ,
             },
             dataType: 'json'
            })
            req.done(function(){
              alert("Updated");
              location.reload();
            });
          })

})
