"use strict";(()=>{(()=>{let t={postMessage:(...e)=>{console.log("Intercepted postMessage in spoofed parent:",e)}};try{Object.defineProperty(window,"parent",{get:()=>t,configurable:!0}),Object.defineProperty(window,"top",{get:()=>t,configurable:!0})}catch(e){console.error("Failed to spoof window.parent/top:",e)}try{Object.defineProperty(document,"referrer",{get:()=>"https://blog.csdn.net/",configurable:!0})}catch(e){console.error("Failed to spoof document.referrer:",e)}let o=document.createElement("style");o.textContent=`
    .passport-header, .login-title, .login-header, .main-header, .header, #header,
    footer, .footer, #footer, .login-footer, .passport-footer,
    #csdn-toolbar, .csdn-toolbar, .toolbar {
      display: none !important;
    }
    .login-container, .login-box, #app, .login-body {
      margin-top: 0 !important;
      padding-top: 0 !important;
    }
    .passport-container-inner {
      height: 100% !important;
    }
  `;let n=()=>{document.head||document.documentElement?(document.head||document.documentElement).appendChild(o):setTimeout(n,1)};n()})();})();
