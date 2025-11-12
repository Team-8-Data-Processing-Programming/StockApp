import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  Dimensions,
  ActivityIndicator,
} from 'react-native';
import PagerView from 'react-native-pager-view';
import StockCard from './StockCard';

const { width } = Dimensions.get('window');
const API_BASE = 'http://172.25.87.185:8000';

const CATEGORY_DEFS = [
  {
    title: '🚀 상승률 TOP10',
    path: '/screen/top-gainers',
    unit: '%',
    metricLabel: '상승률',
  },
  {
    title: '📉 하락률 TOP10',
    path: '/screen/top-losers',
    unit: '%',
    metricLabel: '상승률',
  }, // 표시만 '상승률 -x.x%'로 재활용
  {
    title: '📈 거래량 급증 TOP10',
    path: '/screen/volume-surge',
    unit: '%',
    metricLabel: '거래량증가율',
  },
  {
    title: '📈 3일 연속 상승',
    path: '/screen/three-up',
    unit: '%',
    metricLabel: '상승률',
  },
  {
    title: '💥 급락 후 반등 TOP10',
    path: '/screen/bounce-after-plunge',
    unit: '%',
    metricLabel: '상승률',
  },
  {
    title: '💰 거래대금 TOP10',
    path: '/screen/top-by-trading-value',
    unit: '',
    metricLabel: '거래대금',
  },
  {
    title: '🧱 안정적 우량주 TOP10',
    path: '/screen/stable-bluechips',
    unit: '',
    metricLabel: '변동성',
  },
  {
    title: '💵 배당수익률 TOP10',
    path: '/screen/dividend-yield',
    unit: '%',
    metricLabel: '배당수익률',
  },
  {
    title: '💎 저 PER TOP10',
    path: '/screen/low-per',
    unit: '',
    metricLabel: 'PER',
  },
  {
    title: '📘 저 PBR TOP10',
    path: '/screen/low-pbr',
    unit: '',
    metricLabel: 'PBR',
  },
];

export default function CategorySwiper() {
  const [page, setPage] = useState(0);
  const [pages, setPages] = useState(
    CATEGORY_DEFS.map((c) => ({ ...c, data: [], loading: true, error: null }))
  );

  useEffect(() => {
    (async () => {
      await Promise.all(
        CATEGORY_DEFS.map(async (cat, idx) => {
          try {
            const res = await fetch(`${API_BASE}${cat.path}?limit=10`);
            if (!res.ok) {
              const msg = await res.text();
              throw new Error(`${res.status} ${msg.slice(0, 120)}`);
            }
            const json = await res.json();
            setPages((prev) => {
              const copy = [...prev];
              copy[idx] = {
                ...copy[idx],
                data: json.data || [],
                loading: false,
                error: null,
              };
              return copy;
            });
          } catch (e) {
            setPages((prev) => {
              const copy = [...prev];
              copy[idx] = {
                ...copy[idx],
                loading: false,
                error: `불러오기 실패: ${String(e.message)}`,
              };
              return copy;
            });
          }
        })
      );
    })();
  }, []);

  return (
    <View style={styles.wrapper}>
      <Text style={styles.categoryTitle}>{pages[page]?.title || ''}</Text>
      <PagerView
        style={{ flex: 1 }}
        initialPage={0}
        onPageSelected={(e) => setPage(e.nativeEvent.position)}
      >
        {pages.map((cat, index) => (
          <View key={index} style={styles.page}>
            {cat.loading ? (
              <ActivityIndicator />
            ) : cat.error ? (
              <Text style={{ color: '#fff' }}>{cat.error}</Text>
            ) : (
              <FlatList
                data={cat.data}
                keyExtractor={(item, i) => item.ticker || item.id || String(i)}
                renderItem={({ item, index }) => (
                  <StockCard
                    rank={index + 1}
                    stock={{
                      id: item.ticker || item.id,
                      name: item.name,
                      price: item.price,
                      change: item.change, // % or PER/PBR/거래대금 지표값
                      value: item.value, // 거래대금용
                      unit: cat.unit, // '%'(상승률) 또는 ''
                      metricLabel: cat.metricLabel, // '상승률' | '거래대금' | 'PER' | 'PBR'
                    }}
                  />
                )}
              />
            )}
          </View>
        ))}
      </PagerView>
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: { flex: 1, marginBottom: 24 },
  categoryTitle: {
    color: '#FFFFFF',
    fontSize: 20,
    fontWeight: '700',
    marginBottom: 10,
  },
  page: { width: width, flex: 1 },
});
