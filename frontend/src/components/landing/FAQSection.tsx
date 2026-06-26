import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown } from 'lucide-react';
import ScrollReveal from './ScrollReveal';

const FAQS = [
  { q: 'هل يفهم الذكاء الاصطناعي الدارجة الجزائرية بشكل كامل؟', a: 'آه، فهد مبني خصيصاً على دارجة جزائرية حقيقية — يفهم "واش عندكم؟"، "بكاش؟"، "نبغي نطلب"، "كيفاش التوصيل" وأكثر من 200 صياغة مختلفة يستعملها الزبائن الجزائريين كل يوم. مش chatbot عام مترجَم.' },
  { q: 'كيف يتم استهلاك النقاط من الرصيد الذي اشتريته؟', a: 'نقطة تُحسب فقط على الردود اللي تتم فيها معاملة كاملة — جواب صحيح أو تسجيل طلب. ردود التحويل للإنسان مجانية بالكامل. فهد ما يكلفك غير على النجاح.' },
  { q: 'ماذا يحدث إذا سألني العميل سؤالاً لم تدرب عليه؟', a: 'فهد يعرف حدود معرفته. عندما يواجه سؤال خارج نطاقه، يحول المحادثة ليك فوراً بدون ما يخسر الزبون بردود فارغة. وهذا التحويل مجاني بالكامل.' },
  { q: 'هل يمكنني تحويل المحادثة لموظف بشري في أي وقت؟', a: 'طبعاً. من لوحة التحكم تقدر تفتح "وضع التدخل اليدوي" لأي محادثة وترد أنت مباشرة — وفهد يوقف تلقائياً حتى تعطيه الإذن مرة أخرى.' },
  { q: 'كيف أربط صفحة الفيسبوك أو إنستغرام الخاصة بي؟', a: 'في أقل من دقيقتين — من لوحة التحكم تضغط "ربط صفحة"، تسمح بالصلاحيات المطلوبة، وفهد يبدأ يستقبل الرسائل وي رد عليها بدون أي إعداد تقني.' },
  { q: 'هل المنصة آمنة لبيانات عملائي؟', a: 'نعم. كل البيانات والتوكنات مشفرة باستخدام Fernet encryption. التوكنات ما تنتهيش صلاحيتها. ونحن متوافقون مع متطلبات Meta للأمان.' },
];

export default function FAQSection() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);
  const [allOpen, setAllOpen] = useState(false);

  return (
    <section id="faq" className="landing-faq" style={{ padding: '5rem 4rem', background: 'var(--bg2)' }}>
      <ScrollReveal>
        <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
          <div style={{ fontFamily: "'Cairo',sans-serif", fontSize: '.75rem', fontWeight: 700, color: 'var(--gold)', letterSpacing: '.18em', marginBottom: '.9rem' }}>✦ أسئلة شائعة</div>
          <h2 style={{ fontSize: 'clamp(1.75rem,2.8vw,2.4rem)', fontWeight: 800, lineHeight: 1.25, marginBottom: '.85rem' }}>كل ما تحتاج معرفته عن منصة فهد</h2>
        </div>
      </ScrollReveal>

      <button
        onClick={() => { setAllOpen(!allOpen); setOpenIndex(null); }}
        style={{ display: 'block', margin: '0 auto 1.5rem', background: 'none', border: 'none', color: 'var(--gold)', fontFamily: "'Cairo',sans-serif", fontWeight: 600, fontSize: '.85rem', cursor: 'pointer' }}
      >
        {allOpen ? 'إغلاق الكل' : 'فتح جميع الأسئلة'}
      </button>

      <div style={{ maxWidth: 660, margin: '0 auto' }}>
        {FAQS.map((faq, i) => {
          const isOpen = allOpen || openIndex === i;
          return (
            <ScrollReveal key={i} delay={i * 0.05}>
              <div style={{ borderBottom: '1px solid var(--border)' }}>
                <button
                  onClick={() => { setOpenIndex(isOpen ? null : i); setAllOpen(false); }}
                  style={{ width: '100%', background: 'none', border: 'none', color: 'var(--text)', fontFamily: "'Cairo',sans-serif", fontSize: '.95rem', fontWeight: 600, textAlign: 'right', padding: '1.1rem 0', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '1rem' }}
                >
                  {faq.q}
                  <motion.span animate={{ rotate: isOpen ? 180 : 0 }} transition={{ duration: 0.25 }} style={{ color: 'var(--gold)', fontSize: '.9rem', flexShrink: 0, display: 'flex' }}>
                    <ChevronDown size={16} />
                  </motion.span>
                </button>
                <AnimatePresence>
                  {isOpen && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
                      style={{ overflow: 'hidden' }}
                    >
                      <div style={{ color: 'var(--muted)', fontSize: '.88rem', lineHeight: 1.85, paddingBottom: '1.1rem' }}>{faq.a}</div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </ScrollReveal>
          );
        })}
      </div>
    </section>
  );
}
