import React, { useState, useEffect } from 'react';
import TypeAnimation, { Cursor } from 'react-type-animation';

const TypingAnimation = () => {
  const [isEnglish, setIsEnglish] = useState(true);

  const englishSequence = "Ayurveda is a natural system of medicine that originated in India over 3,000 years ago. It's a branch of Indian science that deals with medicine, herbalism, taxology, anatomy, surgery, and alchemy. The basic literature of Ayurveda, known as Samhita, are written in Sanskrit";
  const sanskritSequence = "आयुर्वेदः भारतीय प्राचीन संस्कृति एवं दर्शन का एक महत्वपूर्ण अंग है। इसे भारतीय उपमहाद्वीप और नेपाल में व्यापक रूप से अमल में लाया जाता है। आयुर्वेद के अनुसार, स्वस्थ रहने का रहस्य नियमित आहार, योग, प्राणायाम, ध्यान, और शारीरिक और मानसिक शुद्धि में है। इसका मुख्य उद्देश्य समग्र स्वास्थ्य और विकास को प्राप्त करना है।";

  // Create a single, combined sequence with a constant speed
  const combinedSequence = isEnglish ? [englishSequence, 70] : [sanskritSequence, 70];

  useEffect(() => {
    const interval = setInterval(() => {
      setIsEnglish(!isEnglish); // Toggle between English and Sanskrit
    }, 10000); // Change text every 10 seconds
    return () => clearInterval(interval);
  }, [isEnglish]);

  return (
    <TypeAnimation
      sequence={combinedSequence}
      cursor={<Cursor blinking={true} />}
      style={{ fontSize: "1.5em", whiteSpace: "pre-wrap", lineHeight: 1.5 }}
    />
  );
};

export default TypingAnimation;
