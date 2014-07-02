function FindProxyForURL(url, host) {
   if (shExpMatch(url,"*.google.com/*")) {
     return "PROXY localhost:8081";
   }

  if (shExpMatch(url,"*.google.com.hk/*")) {
     return "PROXY localhost:8081";
   }

   return "DIRECT; PROXY localhost:8081"; 
}