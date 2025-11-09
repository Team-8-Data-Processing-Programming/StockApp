import React, { useState } from 'react';
import { View, Text, FlatList, StyleSheet, Dimensions } from 'react-native';
import PagerView from 'react-native-pager-view';
import StockCard from './StockCard';

const { width } = Dimensions.get('window');

export default function CategorySwiper() {
  const [page, setPage] = useState(0);

  // 카테고리 목록
  const categories = [
    {
      title: '📊 인기 종목',
      data: [
        { id: '1', name: '삼성전자', price: 71800, change: 1200, rate: 1.7 },
        { id: '2', name: 'SK하이닉스', price: 134500, change: -2500, rate: -1.82 },
        { id: '3', name: 'LG화학', price: 460000, change: 5000, rate: 1.1 },
        { id: '4', name: '카카오', price: 54000, change: -800, rate: -1.46 },
        { id: '5', name: '현대차', price: 220000, change: 2500, rate: 1.15 },
        { id: '6', name: 'LG디스플레이', price: 18300, change: 600, rate: 3.4 },
        { id: '7', name: '기아', price: 97000, change: 1400, rate: 1.47 },
        { id: '8', name: '삼성바이오로직스', price: 720000, change: 4000, rate: 0.56 },
        { id: '9', name: '넷마블', price: 68000, change: -1300, rate: -1.87 },
        { id: '10', name: '신한지주', price: 40000, change: 900, rate: 2.3 }
      ],
    },
    {
      title: '🚀 오늘 가장 많이 오른 종목',
      data: [
        { id: '1', name: '한화솔루션', price: 42000, change: 4000, rate: 10.5 },
        { id: '2', name: '셀트리온', price: 185000, change: 17000, rate: 10.1 },
        { id: '3', name: 'NAVER', price: 195000, change: 15000, rate: 8.3 },
        { id: '4', name: '현대모비스', price: 260000, change: 18000, rate: 7.4 },
        { id: '5', name: '삼성SDI', price: 470000, change: 30000, rate: 6.8 },
        { id: '6', name: 'LG에너지솔루션', price: 420000, change: 25000, rate: 6.3 },
        { id: '7', name: '한미사이언스', price: 54000, change: 2700, rate: 5.3 },
        { id: '8', name: '두산', price: 102000, change: 4800, rate: 4.9 },
        { id: '9', name: '코웨이', price: 62000, change: 2600, rate: 4.4 },
        { id: '10', name: '펄어비스', price: 68000, change: 2800, rate: 4.3 }
      ],
    },
    {
      title: '📈 연속 상승일 기준',
      data: [
        { id: '1', name: 'POSCO홀딩스', price: 480000, change: 2500, rate: 0.5 },
        { id: '2', name: '두산에너빌리티', price: 16000, change: 400, rate: 2.5 },
        { id: '3', name: '현대제철', price: 35000, change: 900, rate: 2.7 },
        { id: '4', name: '한미약품', price: 330000, change: 12000, rate: 3.7 },
        { id: '5', name: 'LG에너지솔루션', price: 420000, change: 8000, rate: 1.9 },
        { id: '6', name: '롯데헬스케어', price: 57000, change: 1700, rate: 3.1 },
        { id: '7', name: '포스코퓨처엠', price: 105000, change: 2300, rate: 2.2 },
        { id: '8', name: 'CJ ENM', price: 91000, change: 2000, rate: 2.3 },
        { id: '9', name: '삼성엔지니어링', price: 39000, change: 1000, rate: 2.6 },
        { id: '10', name: '한국전력', price: 20000, change: 800, rate: 4.1 }
      ],
    },
    {
      title: '🔥 거래량 급등 종목',
      data: [
        { id: '1', name: 'HMM', price: 19000, change: 700, rate: 3.8 },
        { id: '2', name: '롯데케미칼', price: 160000, change: 8000, rate: 5.2 },
        { id: '3', name: '대한항공', price: 31000, change: 1200, rate: 4.0 },
        { id: '4', name: '한온시스템', price: 10500, change: 300, rate: 2.9 },
        { id: '5', name: '아모레퍼시픽', price: 125000, change: -3000, rate: -2.3 },
        { id: '6', name: '한미반도체', price: 30000, change: 1800, rate: 6.4 },
        { id: '7', name: '엔씨소프트', price: 420000, change: 12000, rate: 2.9 },
        { id: '8', name: '삼성전기', price: 145000, change: 3000, rate: 2.1 },
        { id: '9', name: '우리금융지주', price: 14500, change: 400, rate: 2.8 },
        { id: '10', name: '이마트', price: 99000, change: 1500, rate: 1.54 }
      ],
    },
    {
      title: '🌟 이동평균 돌파 (Golden Cross)',
      data: [
        { id: '1', name: 'LG전자', price: 108000, change: 3500, rate: 3.3 },
        { id: '2', name: '현대글로비스', price: 190000, change: 5000, rate: 2.7 },
        { id: '3', name: 'SK이노베이션', price: 160000, change: 4000, rate: 2.6 },
        { id: '4', name: 'KT&G', price: 95000, change: 2000, rate: 2.1 },
        { id: '5', name: 'CJ제일제당', price: 340000, change: 8000, rate: 2.4 },
        { id: '6', name: 'LG생활건강', price: 500000, change: 10000, rate: 2.0 },
        { id: '7', name: '신세계', price: 230000, change: 4000, rate: 1.8 },
        { id: '8', name: '한샘', price: 105000, change: 3500, rate: 3.4 },
        { id: '9', name: '현대백화점', price: 87000, change: 1600, rate: 1.9 },
        { id: '10', name: 'SK바이오사이언스', price: 98000, change: 2800, rate: 2.94 }
      ],
    },
  ];

  return (
    <View style={styles.wrapper}>
      <Text style={styles.categoryTitle}>{categories[page].title}</Text>
      <PagerView
        style={{ flex: 1 }}
        initialPage={0}
        onPageSelected={(e) => setPage(e.nativeEvent.position)}
      >
        {categories.map((cat, index) => (
          <View key={index} style={styles.page}>
            <FlatList
              data={cat.data}
              keyExtractor={(item) => item.id}
              renderItem={({ item, index }) => (
                <StockCard stock={item} rank={index + 1} />
              )}
            />
          </View>
        ))}
      </PagerView>
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: {
    flex: 1,
    marginBottom: 24,
  },
  categoryTitle: {
    color: '#FFFFFF',
    fontSize: 20,
    fontWeight: '700',
    marginBottom: 10,
  },
  page: {
    width: width,
  },
});
