import { motion } from 'framer-motion';
import Card from '../../components/ui/Card';
import { staggerContainer, fadeUp } from '../../animations/variants';

export default function Analytics() {
  return (
    <motion.div variants={staggerContainer} initial="hidden" animate="visible">
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 24 }}>
        <motion.div variants={fadeUp}>
          <Card>
            <h3 style={{ fontSize: '.9rem', fontWeight: 700, marginBottom: 16 }}>أداء المبيعات الشهري</h3>
            <div style={{ display:'flex', alignItems:'center', justifyContent:'center', height:280, color:'var(--muted)', fontSize:'.85rem' }}>
              لا توجد بيانات مبيعات كافية بعد. ابدأ في استقبال الطلبات وستظهر الإحصائيات هنا.
            </div>
          </Card>
        </motion.div>

        <motion.div variants={fadeUp} transition={{ delay: 0.08 }}>
          <Card>
            <h3 style={{ fontSize: '.9rem', fontWeight: 700, marginBottom: 16 }}>المحادثات والطلبات</h3>
            <div style={{ display:'flex', alignItems:'center', justifyContent:'center', height:280, color:'var(--muted)', fontSize:'.85rem' }}>
              لا توجد بيانات كافية بعد لعرض المخطط.
            </div>
          </Card>
        </motion.div>
      </div>

      <motion.div variants={fadeUp}>
        <Card>
          <h3 style={{ fontSize: '.9rem', fontWeight: 700, marginBottom: 16 }}>أفضل المنتجات مبيعاً</h3>
          <div style={{ display:'flex', alignItems:'center', justifyContent:'center', height:160, color:'var(--muted)', fontSize:'.85rem' }}>
            لا توجد منتجات مبيعة بعد.
          </div>
        </Card>
      </motion.div>
    </motion.div>
  );
}
