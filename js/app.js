$(function(){       

        var recipients = [];
        var isAllselected = false;

        $(window).resize(function(){
          setScrollableDivHeight();
        });

        var setScrollableDivHeight = function(){
          var scrollableDivHeight = $(window).height() - 338;        
          $('.scrollablediv').css('height', scrollableDivHeight);
        }

        setScrollableDivHeight();

        var addrecipient = function(recipient){
          isRecipientAdded = false;
          
          $.each(recipients,function(index,patient){
              if (patient.name == recipient.name && patient.email == recipient.email) {
                    isRecipientAdded = true;
              };
          })
          
          if (!isRecipientAdded) {                        
            recipients.push(recipient);
            addRecipientToMessageBox();
          };
        }

        var removerecipient = function(recipient){
          //console.log(JSON.stringify(recipient));
          $.each(recipients,function(index,patient){             
             try{
                if (patient.name == recipient.name && patient.email == recipient.email ) {
                      recipients.splice(recipients.indexOf(patient),1);
                };
            }
            catch(error){}
          });
          addRecipientToMessageBox();
        }

        var closeDisplayingMessage = function(){
            $("#messagecontentcont").addClass('hide');
        }


        var addRecipientToMessageBox = function(){
          var rcpnts = "";
          //console.log(recipients);
          
          $.each(recipients,function(index,patient){
            rcpnts = rcpnts + patient.name.toString() +"<"+ patient.email.toString() +">"+",";
          });

          $("#recipients_box").text(rcpnts);
        }


        $('#messageclose').click(function(){
          closeDisplayingMessage();
        });

        $('.mail').click(function(){
          $("#messagecontentcont").removeClass('hide');
          var e_mail = {}

          $(this).children('.mail_to').each(function(i,el){
            e_mail.to ='To: ' + $(this).text();
            e_mail.from = 'From: ' + $(this).attr('from');
          });

          $(this).children('.mail_content').each(function(i,el){
            e_mail.content = $(this).text();
          });

          console.log(e_mail);
          
          $('#message_to').text(e_mail.to);
          $('#message_from').text(e_mail.from);
          $('#message_cont').text(e_mail.content);

        })

        $('.select').click(function(){
          var pat = $(this).parent().parent().children(".patient-info");
          var pat_info = {name:pat.children("h4").text(),email:pat.children(".email_add").text()}

          if ($(this).prop('checked') == false) {
            console.log(JSON.stringify(pat_info));
            removerecipient(pat_info);                
          }

          else{
            var emailid_pattern = /^\w+@[a-zA-Z_]+?\.[a-zA-Z]{2,3}$/;

            if (!pat_info.email.match(emailid_pattern)) {                  
              alert("This patient do not have a valid e-mail address");
              $(this).prop('checked',false);
              return;
            }

            else{
              addrecipient(pat_info);
            }
          }
          console.log(JSON.stringify(recipients));

        });

        $('#selectall').click(function(){
          recipients = [];

          if ($('#selectall').prop('checked') == false) {           
              var temp = $('.select').prop('checked',false);              
          }

          else {            
              var temp = $('.select').prop('checked',true);                
              $('.patient-info').each(function(index,element){
                  if ($(this).children('.email_add').text()) {                 
                      recipients.push({name:$(this).children("h4").text(),email:$(this).children(".email_add").text()});
                  }
              });                            
          }
          addRecipientToMessageBox();
        });



        // if ($('.select').prop('checked') == true){
        //   console.log(this)
        // }

        $('#msgmin').click(function(){
          $('.messagecomposercont').toggleClass('minimize');
          $('.messagecomposerbox').toggleClass('hide');
          $('.messagecomposerfooter').toggleClass('hide');
        });

        $('#msgcls').click(function(){
          $('.messagecomposercont').removeClass('minimize');
          $('.messagecomposerbox').removeClass('hide');
          discardNewMessage();

        });

        $('#composemail').click(function(){         
          $('.messagecomposercont').removeClass('hide');
        });


        $("#send_message").click(function(e){
  

          if (recipients.length <= 0) {
            alert("Please enter at least one patient email address");
            return;
          };
          
          var email_content = {};
          email_content.To = recipients;
          email_content.email_sub = $("#email_subject").val();
          email_content.email_text = $("#email_text_box").val();

          if (!email_content.email_text) {
            alert("Cannot send empty messages");
            return;
          };
          
          $(".messagecomposercont").addClass('hide');

          $.ajax({
            url:"/sendMessage",
            type:"post",
            data:{mail:JSON.stringify(email_content)},           
            beforeSend:function(){
              //console.log(recipients);              
            },
            success:function(d){
              alert("Message has been successfully sent!");
              discardNewMessage();
            },
            error:function(){
              //console.log("error!");
              alert("Error occurred while attempting to send the message. Please send it again");
              $(".messagecomposercont").removeClass('hide');
            }
          })
        });

        var discardNewMessage = function(){
          $(".select").prop('checked',false);
           $("#selectall").prop('checked',false)
          $(".messagecomposercont").addClass('hide');
          $("#email_subject").val('');
          $("#email_text_box").val('');
          $("#recipients_box").val('');
          recipients = [];
        }
});