/* Meta pixel for Finnian ads (dataset "Finnian Pixel", portfolio Finnian).

   PageView on every page that loads this, plus one custom event,
   ListenClick, when someone clicks through to a streaming or store link.
   Ads optimise on ListenClick (a custom conversion filtered on
   service = spotify), because Spotify itself cannot hold a pixel.

   The click waits ~200ms before navigating so the event leaves the page;
   a new-tab or modified click is left alone. */
(function () {
  var PIXEL_ID = "2297676037687688";

  !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?
  n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;
  n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;
  t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,
  document,'script','https://connect.facebook.net/en_US/fbevents.js');

  fbq("init", PIXEL_ID);
  fbq("track", "PageView");

  var SERVICES = [
    ["open.spotify.com", "spotify"],
    ["music.apple.com", "apple"],
    ["soundcloud.com", "soundcloud"],
    ["bandcamp.com", "bandcamp"],
    ["deezer.com", "deezer"],
    ["music.amazon.", "amazon"],
    ["tidal.com", "tidal"],
    ["youtube.com", "youtube"],
    ["youtu.be", "youtube"],
    ["hypeddit.com", "hypeddit"]
  ];

  function serviceFor(href) {
    for (var i = 0; i < SERVICES.length; i++) {
      if (href.indexOf(SERVICES[i][0]) !== -1) return SERVICES[i][1];
    }
    return null;
  }

  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a[href]");
    if (!a) return;
    var service = serviceFor(a.href);
    if (!service) return;
    var page = location.pathname;
    fbq("trackCustom", "ListenClick", { service: service, page: page });
    if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey ||
        e.shiftKey || e.altKey || a.target === "_blank") return;
    e.preventDefault();
    setTimeout(function () { location.href = a.href; }, 200);
  });
})();
