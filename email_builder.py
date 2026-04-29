import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SENDER_EMAIL = os.getenv("SENDER_EMAIL")


def build_email_template(to, form_url):
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = to
    msg["Subject"] = "Avaliação do Sono - Formulário de Pesquisa"

    html = f"""
       <!DOCTYPE html>
       <html lang="pt-BR">
       <head>
           <meta charset="UTF-8">
           <meta name="viewport" content="width=device-width, initial-scale=1.0">
           <title>Avaliação do Sono</title>
       </head>
       <body style="margin:0; padding:0; background-color:#f4f6f8;">
           <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#f4f6f8; padding:20px 0;">
               <tr>
                   <td align="center">
                       <table width="600" cellpadding="0" cellspacing="0" border="0" 
                              style="background:#ffffff; border-radius:8px; overflow:hidden; font-family:Arial, sans-serif;">

                           <tr>
                               <td style="background:#2c3e50; color:#ffffff; padding:20px; text-align:center;">
                                   <h1 style="margin:0; font-size:22px;">Avaliação do Sono, Saúde mental e Risco de Lesões em Corredores</h1>
                                   <p style="margin:5px 0 0; font-size:14px;">Pesquisa de acompanhamento</p>
                               </td>
                           </tr>

                           <tr>
                               <td style="padding:30px; color:#333;">
                                   <p style="margin-top:0;">Olá,</p>

                                   <p>
                                       Agradecemos pela sua participação na nossa
                                       <strong>Pesquisa de Iniciação Científica sobre Avaliação do Sono, Saúde mental e Risco de Lesões em Corredores.</strong>.
                                   </p>

                                   <p>
                                       Para garantir a continuidade e qualidade da pesquisa, é essencial que você continue respondendo aos formulários que enviaremos por e-mail.
                                       Sua contribuição nos ajuda a entender cada vez mais sobre esse esporte que tanto amamos.
                                   </p>

                                   <!-- Button -->
                                   <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:30px 0;">
                                       <tr>
                                           <td align="center">
                                               <a href="{form_url}"
                                                  style="background-color:#27ae60; color:#ffffff; padding:14px 24px; 
                                                         text-decoration:none; border-radius:6px; font-weight:bold;
                                                         display:inline-block;">
                                                   Acessar Formulário
                                               </a>
                                           </td>
                                       </tr>
                                   </table>

                                   <p>
                                       Caso tenha dúvidas ou dificuldades, nossa equipe está a disposição para ajudar.
                                   </p>

                                   <p style="margin-bottom:0;">
                                       Atenciosamente,<br>
                                       <strong>Equipe de Pesquisa de Iniciação Científica sobre Avaliação do Sono, Saúde mental e Risco de Lesões em Corredores.</strong>
                                   </p>
                               </td>
                           </tr>

                           <!-- Footer -->
                           <tr>
                               <td style="background:#ecf0f1; padding:15px; text-align:center; font-size:12px; color:#777;">
                                   Este é um e-mail automático. Por favor, não responda diretamente a esta mensagem.
                               </td>
                           </tr>

                       </table>
                   </td>
               </tr>
           </table>
       </body>
       </html>
       """

    msg.attach(MIMEText(html, "html"))
    return msg
