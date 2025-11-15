import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  Modal,
  Pressable,
  FlatList,
  StyleSheet,
  Dimensions,
  ActivityIndicator,
  TouchableOpacity
} from 'react-native';
import PagerView from 'react-native-pager-view';
import StockCard from './StockCard';

const { width } = Dimensions.get('window');
const API = 'http://192.168.45.24:8000';

const CATEGORY_DEFS = [
  {
    title: '🚀 상승률 TOP10',
    description: '오늘 하루 기준으로 주가가 가장 많이 오른 종목 10개를 등락률(%) 순으로 보여줍니다.',
    path: '/screen/top-gainers',
    unit: '%',
    metricLabel: '상승률',
  },
  {
    title: '📉 하락률 TOP10',
    description: '오늘 하루 기준으로 주가가 가장 많이 떨어진 종목 10개를 등락률(%) 순으로 보여줍니다.',
    path: '/screen/top-losers',
    unit: '%',
    metricLabel: '상승률',
  }, // 표시만 '상승률 -x.x%'로 재활용
  {
    title: '📈 거래량 급증 TOP10',
    description: '전날보다 거래량이 몇 %나 늘었는지 계산해서, 거래량 증가율이 가장 큰 종목 10개를 보여줍니다.',
    path: '/screen/volume-surge',
    unit: '%',
    metricLabel: '거래량증가율',
  },
  {
    title: '📈 3일 연속 상승',
    description: '최근 4영업일 동안 가격이 매일 조금씩 올라온 종목들 중에서, 상승률이 큰 종목 10개를 보여줍니다.',
    path: '/screen/three-up',
    unit: '%',
    metricLabel: '상승률',
  },
  {
    title: '💥 급락 후 반등 TOP10',
    description: '전날에는 -3% 이상 크게 떨어졌지만 오늘은 다시 플러스(상승)로 돌아선 종목 중, 반등 폭이 큰 10개를 보여줍니다.',
    path: '/screen/bounce-after-plunge',
    unit: '%',
    metricLabel: '상승률',
  },
  {
    title: '💰 거래대금 TOP10',
    description: '“가격 × 거래량”으로 계산한 거래대금이 가장 큰 종목 10개를 보여줘서, 실제 돈이 많이 오간 종목을 한눈에 볼 수 있게 합니다.',
    path: '/screen/top-by-trading-value',
    unit: '',
    metricLabel: '거래대금',
  },
  {
    title: '🧱 안정적 우량주 TOP10',
    description: ' 시가총액 상위 종목들 가운데 최근 20영업일 동안 가격 출렁임(변동성)이 가장 작은 종목 10개를 골라, 비교적 안정적인 대형주를 보여줍니다.',
    path: '/screen/stable-bluechips',
    unit: '',
    metricLabel: '변동성',
  },
  {
    title: '💵 배당수익률 TOP10',
    description: '주가 대비 배당금 비율(DIV)이 높은 순서대로, 배당수익률이 가장 높은 종목 10개를 보여줍니다.',
    path: '/screen/dividend-yield',
    unit: '%',
    metricLabel: '배당수익률',
  },
  {
    title: '💎 저 PER TOP10',
    description: '이익 대비 주가 수준을 나타내는 PER이 양수이면서 가장 낮은 종목 10개를 골라, 이익에 비해 비교적 싸게 거래되는 종목을 보여줍니다.',
    path: '/screen/low-per',
    unit: '',
    metricLabel: 'PER',
  },
  {
    title: '📘 저 PBR TOP10',
    description: '자산 대비 주가 수준을 나타내는 PBR이 양수이면서 가장 낮은 종목 10개를 골라, 보유 자산에 비해 저평가된 종목을 보여줍니다.',
    path: '/screen/low-pbr',
    unit: '',
    metricLabel: 'PBR',
  },
];

export default function CategorySwiper() {
  const [page, setPage] = useState(0);
  const [modalVisible, setModalVisible] = useState(false);
  const [currentDescription, setCurrentDescription] = useState('');
  const [pages, setPages] = useState(
    CATEGORY_DEFS.map((c) => ({ ...c, data: [], loading: true, error: null }))
  );

  useEffect(() => {
    (async () => {
      await Promise.all(
        CATEGORY_DEFS.map(async (cat, idx) => {
          try {
            const res = await fetch(`${API}${cat.path}?limit=10`);
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
      <View style={styles.titleRow}>
        <Text style={styles.categoryTitle}>{pages[page]?.title || ''}</Text>
        <Text
          style={styles.helpIcon}
          onPress={() => {
            setCurrentDescription(pages[page]?.description || '');
            setModalVisible(true);
          }}
        >
          ℹ️
        </Text>
      </View>

      <Modal
        visible={modalVisible}
        transparent={true}
        animationType="fade"
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalBox}>
            <Text style={styles.modalTitle}>설명</Text>
            <Text style={styles.modalContent}>{currentDescription}</Text>
            <Pressable
              style={styles.closeButton}
              onPress={() => setModalVisible(false)}
            >
              <Text style={styles.closeButtonText}>닫기</Text>
            </Pressable>
          </View>
        </View>
      </Modal>

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
  titleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'flex-start',
    marginBottom: 10,
  },
  helpIcon: {
    marginLeft: 8,
    color: '#ccc',
    fontSize: 18,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.6)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalBox: {
    width: '80%',
    backgroundColor: '#1E2336',
    borderRadius: 16,
    padding: 20,
    alignItems: 'center',
  },
  modalTitle: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 10,
  },
  modalContent: {
    color: '#B0B3C2',
    fontSize: 15,
    textAlign: 'center',
    marginBottom: 20,
  },
  closeButton: {
    backgroundColor: '#7c3aed',
    borderRadius: 10,
    paddingVertical: 8,
    paddingHorizontal: 20,
  },
  closeButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});
