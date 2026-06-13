import { useEffect, useState } from 'react';
import { animate } from 'motion/react';

/** Eases a number from 0 → value once on mount and whenever value changes. */
export function useCountUp(value: number, duration = 0.9): number {
  const [display, setDisplay] = useState(0);
  useEffect(() => {
    const controls = animate(0, value, {
      duration,
      ease: [0.22, 1, 0.36, 1],
      onUpdate: (v) => setDisplay(v),
    });
    return () => controls.stop();
  }, [value, duration]);
  return display;
}
