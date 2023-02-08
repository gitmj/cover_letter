import streamlit.components.v1 as components
components.html(
    f'<script src="https://donorbox.org/widget.js" paypalExpress="false"></script><iframe src="https://donorbox.org/embed/effective-cover-letters?default_interval=o&amount=1" name="donorbox" allowpaymentrequest="allowpaymentrequest" seamless="seamless" frameborder="0" scrolling="auto" height="900px" width="100%" style="max-width: 500px; min-width: 250px; max-height:none!important"></iframe>',
    height=650,
    )   
