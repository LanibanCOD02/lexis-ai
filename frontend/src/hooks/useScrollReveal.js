import { useEffect, useRef, useState } from 'react';

export function useScrollReveal(options = { threshold: 0.1, rootMargin: '0px 0px -50px 0px' }) {
  const [isVisible, setIsVisible] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    // Check for reduced motion preference
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    
    // If user prefers reduced motion, just set visible immediately
    if (mediaQuery.matches) {
      setIsVisible(true);
      return;
    }

    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        setIsVisible(true);
        // Optional: unobserve after revealing if we only want it to animate once
        if (ref.current) {
          observer.unobserve(ref.current);
        }
      }
    }, options);

    const currentRef = ref.current;
    if (currentRef) {
      observer.observe(currentRef);
    }

    return () => {
      if (currentRef) {
        observer.unobserve(currentRef);
      }
    };
  }, [options.threshold, options.rootMargin]);

  return [ref, isVisible];
}

export const useParallax = (speed = 0.5) => {
  const [offset, setOffset] = useState(0);
  const ref = useRef(null);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    if (mediaQuery.matches) return;

    let rafId;
    const handleScroll = () => {
      if (!ref.current) return;
      const rect = ref.current.getBoundingClientRect();
      if (rect.top < window.innerHeight && rect.bottom > 0) {
        const scrollDist = window.innerHeight - rect.top;
        setOffset(scrollDist * speed);
      }
    };

    const onScroll = () => {
      cancelAnimationFrame(rafId);
      rafId = requestAnimationFrame(handleScroll);
    };

    window.addEventListener('scroll', onScroll, { passive: true });
    handleScroll();

    return () => {
      window.removeEventListener('scroll', onScroll);
      cancelAnimationFrame(rafId);
    };
  }, [speed]);

  return [ref, offset];
}

// Cinematic Parallax Hook for Scroll and Mouse
export const useCinematicParallax = () => {
  const containerRef = useRef(null);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    if (mediaQuery.matches) return;

    let rafId;
    let targetScroll = window.scrollY;
    let currentScroll = window.scrollY;
    
    let targetMouseX = 0;
    let targetMouseY = 0;
    let currentMouseX = 0;
    let currentMouseY = 0;

    const handleScroll = () => {
      targetScroll = window.scrollY;
    };

    const handleMouseMove = (e) => {
      // Normalize mouse coordinates to -1 to 1 based on window center
      targetMouseX = (e.clientX / window.innerWidth - 0.5) * 2;
      targetMouseY = (e.clientY / window.innerHeight - 0.5) * 2;
    };

    const animate = () => {
      // Smooth interpolation for scroll
      currentScroll += (targetScroll - currentScroll) * 0.1;
      
      // Cap scroll impact to prevent infinite drifting away
      // Hero is 100vh, so max scroll is roughly window.innerHeight
      const maxScroll = window.innerHeight * 1.5; 
      const cappedScroll = Math.min(currentScroll, maxScroll);
      
      // Smooth interpolation for mouse
      currentMouseX += (targetMouseX - currentMouseX) * 0.05;
      currentMouseY += (targetMouseY - currentMouseY) * 0.05;

      if (containerRef.current) {
        containerRef.current.style.setProperty('--scroll-y', `${cappedScroll}`);
        containerRef.current.style.setProperty('--mouse-x', `${currentMouseX}`);
        containerRef.current.style.setProperty('--mouse-y', `${currentMouseY}`);
      }

      rafId = requestAnimationFrame(animate);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    
    // Only enable mouse parallax on non-touch devices
    if (window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
      window.addEventListener('mousemove', handleMouseMove, { passive: true });
    }

    animate();

    return () => {
      window.removeEventListener('scroll', handleScroll);
      window.removeEventListener('mousemove', handleMouseMove);
      cancelAnimationFrame(rafId);
    };
  }, []);

  return containerRef;
};
