var requestNextAnimationFrame = (function () {
  "use strict";
  var queue = [];
  var requested;

  var go = function (t) {
    var this_queue = queue.slice();
    queue = [];
    requested = false;
    for (var i = 0; i < this_queue.length; i++) {
      this_queue[i](t);
    }
  };

  var delay = function () {
    requestAnimationFrame(go);
  };

  return function (f) {
    queue.push(f);
    if (!requested) {
      requestAnimationFrame(delay);
    }
    requested = true;
  };
})();

var Fx = (function () {
  "use strict";
  var self = {};

  self.transform = (function () {
    var transforms = [
      "transform",
      "WebkitTransform",
      "msTransform",
      "MozTransform",
    ];
    var p = transforms.shift();
    var t = document.createElement("div");
    while (p) {
      if (typeof t.style[p] !== "undefined") {
        return p;
      }
      p = transforms.shift();
    }
  })();

  // this never really worked 100% of the time, leaving lots of leftover elements
  // self.chain_transition = function(el, end_func) {
  // 	var end_func_wrapper = function(e) {
  // 		end_func(e, el);
  // 		el.removeEventListener("transitionend", end_func_wrapper, false);
  // 	};
  // 	el.addEventListener("transitionend", end_func_wrapper, false);
  // };

  self.remove_element = function (el) {
    if (document.body.classList.contains("loading")) {
      if (el.parentNode) el.parentNode.removeChild(el);
    } else {
      // self.chain_transition(el,
      // 	function() {
      // 		if (el.parentNode) {
      // 			el.parentNode.removeChild(el);
      // 		}
      // 	}
      // );
      setTimeout(function () {
        if (el.parentNode) {
          el.parentNode.removeChild(el);
        }
      }, 1000);
      requestNextAnimationFrame(function () {
        el.style.opacity = 0;
      });
    }
  };

  return self;
})();
