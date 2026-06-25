import { ReactNode } from 'react';
import { motion } from 'framer-motion';
import { fadeUp } from '../../animations/variants';
import useScrollReveal from '../../animations/useScrollReveal';

interface Props {
  children: ReactNode;
  delay?: number;
  className?: string;
  style?: React.CSSProperties;
}

export default function ScrollReveal({ children, delay = 0, className, style }: Props) {
  const { ref, revealed } = useScrollReveal(0.1);

  return (
    <motion.div
      ref={ref}
      variants={fadeUp}
      initial="hidden"
      animate={revealed ? 'visible' : 'hidden'}
      transition={{ delay }}
      className={className}
      style={style}
    >
      {children}
    </motion.div>
  );
}
