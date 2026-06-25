import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Coins, CreditCard, Zap, TrendingUp, ChevronDown } from 'lucide-react';
import client from '../../api/client';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import Badge from '../../components/ui/Badge';
import Modal from '../../components/ui/Modal';
import { staggerContainer, fadeUp } from '../../animations/variants';
import { showToast } from '../../components/ui/Toast';

const PACKS = [
  { name: 'ستارتر', credits: 5000, price: 2500, ht: 2125, tva: 375, popular: false },
  { name: 'بيزنس', credits: 15000, price: 6000, ht: 5085, tva: 915, popular: true },
  { name: 'برو', credits: 50000, price: 18000, ht: 15254, tva: 2746, popular: false },
];

export default function Credits() {
  const [balance, setBalance] = useState(0);
  const [showBuy, setShowBuy] = useState(false);
  const [selectedPack, setSelectedPack] = useState<typeof PACKS[0] | null>(null);

  useEffect(() => {
    client.get('/api/auth/me').then(r => setBalance(r.data?.credits || 0)).catch(() => {});
  }, []);

  const handleBuy = (pack: typeof PACKS[0]) => {
    setSelectedPack(pack);
    setShowBuy(true);
  };

  const confirmBuy = () => {
    showToast('success', `تم شراء ${selectedPack?.credits?.toLocaleString()} نقطة بنجاح`);
    setShowBuy(false);
    setBalance(prev => prev + (selectedPack?.credits || 0));
  };

  return (
    <motion.div variants={staggerContainer} initial="hidden" animate="visible">
      <motion.div variants={fadeUp}>
        <Card style={{ textAlign: 'center', marginBottom: 24, padding: '2.5rem' }}>
          <div style={{ width: 56, height: 56, borderRadius: 16, background: 'rgba(232,168,48,0.12)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1rem' }}>
            <Coins size={28} style={{ color: 'var(--gold)' }} />
          </div>
          <div style={{ fontFamily: "'Cairo',sans-serif", fontSize: '3rem', fontWeight: 900, color: 'var(--gold)', lineHeight: 1 }}>
            {balance.toLocaleString()}
          </div>
          <div style={{ fontSize: '.85rem', color: 'var(--muted)', marginBottom: 16 }}>الرصيد المتبقي</div>
          <div style={{ maxWidth: 300, margin: '0 auto 16px' }}>
            <div style={{ height: 8, background: 'var(--bg3)', borderRadius: 4, overflow: 'hidden' }}>
              <div style={{ width: `${Math.min((balance / 100000) * 100, 100)}%`, height: '100%', background: 'linear-gradient(90deg, var(--gold), var(--terra))', borderRadius: 4, transition: 'width 1s ease-out' }} />
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '.7rem', color: 'var(--faint)', marginTop: 4 }}>
              <span>مستهلك: {Math.max(0, 100000 - balance).toLocaleString()}</span>
              <span>الحد: 100,000</span>
            </div>
          </div>
          <Button onClick={() => setShowBuy(true)} size="lg">شحن الرصيد ←</Button>
        </Card>
      </motion.div>

      <motion.div variants={fadeUp}>
        <Card style={{ marginBottom: 24 }}>
          <h3 style={{ fontSize: '.9rem', fontWeight: 700, marginBottom: 16 }}>المعاملات</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {[
              { date: '2026-06-25', desc: 'شراء رصيد — بيزنس', amount: 15000, balanceAfter: 15000 },
              { date: '2026-06-24', desc: 'استهلاك ردود', amount: -230, balanceAfter: 14770 },
              { date: '2026-06-23', desc: 'استهلاك ردود', amount: -185, balanceAfter: 14585 },
              { date: '2026-06-22', desc: 'تسجيل طلبات', amount: -45, balanceAfter: 14540 },
            ].map((t, i) => (
              <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 0', borderBottom: i < 3 ? '1px solid var(--border)' : 'none' }}>
                <div>
                  <div style={{ fontSize: '.82rem', fontWeight: 600 }}>{t.desc}</div>
                  <div style={{ fontSize: '.72rem', color: 'var(--muted)' }}>{t.date}</div>
                </div>
                <div style={{ textAlign: 'left' }}>
                  <div style={{ fontFamily: "'Cairo',sans-serif", fontWeight: 700, fontSize: '.85rem', color: t.amount > 0 ? 'var(--success)' : 'var(--danger)' }}>
                    {t.amount > 0 ? '+' : ''}{t.amount.toLocaleString()}
                  </div>
                  <div style={{ fontSize: '.72rem', color: 'var(--muted)' }}>{t.balanceAfter.toLocaleString()} ←</div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </motion.div>

      <motion.div variants={staggerContainer} style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 16 }}>
        {PACKS.map((pack, i) => (
          <motion.div key={pack.name} variants={fadeUp} transition={{ delay: i * 0.08 }}>
            <Card gold={pack.popular} hover style={{ textAlign: 'center', position: 'relative', overflow: 'visible' }}>
              {pack.popular && (
                <div style={{ position: 'absolute', top: -11, left: '50%', transform: 'translateX(-50%)', background: 'var(--gold)', color: 'var(--bg)', fontFamily: "'Cairo',sans-serif", fontSize: '.68rem', fontWeight: 700, padding: '.2rem .9rem', borderRadius: 100 }}>
                  الأكثر شيوعاً
                </div>
              )}
              <div style={{ fontFamily: "'Cairo',sans-serif", fontSize: '.85rem', fontWeight: 700, color: 'var(--muted)', marginBottom: '.5rem' }}>{pack.name}</div>
              <div style={{ fontFamily: "'Cairo',sans-serif", fontSize: '2.4rem', fontWeight: 900, lineHeight: 1, color: 'var(--gold)', marginBottom: '.25rem' }}>
                {pack.price.toLocaleString()} <sub style={{ fontSize: '1rem', fontWeight: 400, color: 'var(--muted)' }}>دج</sub>
              </div>
              <div style={{ fontSize: '.88rem', color: 'var(--muted)', marginBottom: '1rem' }}>{pack.credits.toLocaleString()} نقطة</div>
              <div style={{ fontSize: '.7rem', color: 'var(--faint)', marginBottom: '1rem' }}>
                ش ق م: {pack.ht.toLocaleString()} دج | TVA: {pack.tva} دج
              </div>
              <Button variant={pack.popular ? 'gold' : 'outline'} style={{ width: '100%' }} onClick={() => handleBuy(pack)}>اشترِ الآن</Button>
            </Card>
          </motion.div>
        ))}
      </motion.div>

      <Modal open={showBuy} onClose={() => setShowBuy(false)} title="تأكيد الشراء">
        {selectedPack && (
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '.85rem', color: 'var(--muted)', marginBottom: 8 }}>باقة {selectedPack.name}</div>
            <div style={{ fontFamily: "'Cairo',sans-serif", fontSize: '2rem', fontWeight: 900, color: 'var(--gold)' }}>
              {selectedPack.credits.toLocaleString()} نقطة
            </div>
            <div style={{ fontSize: '.9rem', color: 'var(--muted)', marginBottom: 16 }}>
              {selectedPack.price.toLocaleString()} دج (ش ق م: {selectedPack.ht} دج + TVA: {selectedPack.tva} دج)
            </div>
            <div style={{ background: 'var(--bg3)', borderRadius: 12, padding: '1rem', marginBottom: 16, fontSize: '.82rem', color: 'var(--muted)' }}>
              <p>سيتم إضافة {selectedPack.credits.toLocaleString()} نقطة إلى رصيدك فوراً.</p>
              <p style={{ marginTop: 4 }}>الرصيد الحالي: {balance.toLocaleString()} ← الرصيد بعد الشراء: {(balance + selectedPack.credits).toLocaleString()}</p>
            </div>
            <div style={{ display: 'flex', gap: 8 }}>
              <Button variant="outline" style={{ flex: 1 }} onClick={() => setShowBuy(false)}>إلغاء</Button>
              <Button style={{ flex: 1 }} onClick={confirmBuy}>تأكيد الشراء</Button>
            </div>
          </div>
        )}
      </Modal>
    </motion.div>
  );
}
