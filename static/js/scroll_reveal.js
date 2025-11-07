(function () {
      const ease = 'cubic-bezier(0.2, 0.65, 0.3, 1)';
      const baseDurationMs = 1000; // entrance animation duration
      const baseDistancePx = 60;  // noticeable movement
      const staggerMs = 70;       // slight stagger

      const setups = [
        { selector: '.home-image', origin: 'left' },
        { selector: '.home-text .hidden', origin: 'right', unhide: true },
        { selector: '.events-title', origin: 'bottom', unhide: true },
        { selector: '.carousel-slide', origin: 'bottom', rotateY: 6 },
        { selector: '.about .hidden', origin: 'bottom', unhide: true },
        { selector: '.about img', origin: 'right' },
        { selector: '.prior-cabinets-title', origin: 'bottom', unhide: true },
        { selector: '.prior-cabinets-container', origin: 'bottom' },
        { selector: '.cabinet-card', origin: 'bottom' },
        { selector: '.footer', origin: 'bottom' }
      ];

      const computeTransform = (origin, distance, rotateY) => {
        const shift = (axis, val) => axis === 'x' ? `translateX(${val}px)` : `translateY(${val}px)`;
        let axis = 'y';
        if (origin === 'left' || origin === 'right') axis = 'x';
        const sign = (origin === 'left' || origin === 'top') ? -1 : 1;
        const base = shift(axis, sign * distance);
        const rot = rotateY ? ` rotateY(${rotateY}deg)` : '';
        return base + rot;
      };

      const prime = (el, origin, rotateY) => {
        el.style.opacity = '0';
        el.style.transform = computeTransform(origin, baseDistancePx, rotateY);
        el.style.transition = `transform ${baseDurationMs}ms ${ease}, opacity ${baseDurationMs}ms ${ease}`;
        el.style.willChange = 'transform, opacity';
      };

      const show = (el, unhide) => {
        if (unhide && el.classList) el.classList.remove('hidden');
        el.style.opacity = '1';
        el.style.transform = 'translateX(0) translateY(0)';
        // After entrance finishes, hand control back to CSS (hover transitions)
        setTimeout(() => {
          el.style.removeProperty('transform');
          el.style.removeProperty('transition');
          el.style.removeProperty('will-change');
          el.style.removeProperty('opacity');
        }, baseDurationMs + 50);
      };

      const io = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          const el = entry.target;
          const meta = el.__revealMeta || {};
          setTimeout(() => show(el, !!meta.unhide), meta.delay || 0);
          io.unobserve(el);
        });
      }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });

      setups.forEach(({ selector, origin, unhide, rotateY }) => {
        const nodes = document.querySelectorAll(selector);
        nodes.forEach((el, idx) => {
          // avoid double-priming if script injected twice
          if (el.__revealPrimed) return;
          el.__revealPrimed = true;
          prime(el, origin, rotateY);
          el.__revealMeta = { unhide, delay: idx * staggerMs };
          io.observe(el);
        });
      });
    })();