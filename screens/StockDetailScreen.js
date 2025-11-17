// screens/StockDetailScreen.js
import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
} from 'react-native';

const API = 'http://172.30.1.84:8000';

export default function StockDetailScreen({ route }) {
  const { stockName, ticker } = route.params;

  const [stockData, setStockData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStockDetail = async () => {
      try {
        console.log(`[요청 URL] ${API}/stock/detail?ticker=${ticker}`);
        const res = await fetch(`${API}/stock/detail?ticker=${ticker}`);
        console.log('[응답 상태]', res.status);
        const json = await res.json();
        console.log('[StockDetail API 응답]', json);
        setStockData(json);
      } catch (err) {
        console.log('[에러 발생]', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchStockDetail();
  }, [ticker]);

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#7c3aed" />
        <Text style={{ color: '#fff', marginTop: 10 }}>불러오는 중...</Text>
      </View>
    );
  }

  if (error || !stockData) {
    return (
      <View style={styles.center}>
        <Text style={{ color: '#fff' }}>데이터를 불러오지 못했습니다.</Text>
      </View>
    );
  }

  const infoItems = [
    { label: '시가총액', value: stockData.marketCap },
    { label: '배당수익률', value: `${stockData.dividendYield?.toFixed(2)}%` },
    { label: 'PBR', value: stockData.pbr?.toFixed(1) },
    { label: 'PER', value: stockData.per?.toFixed(1) },
    { label: 'ROE', value: `${stockData.roe?.toFixed(1)}%` },
  ];

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={{ paddingBottom: 40 }}
    >
      <Text style={styles.title}>📊 {stockData.name}</Text>

      <View style={styles.priceRow}>
        <Text style={styles.price}>{stockData.price?.toLocaleString()}원</Text>
        <Text
          style={[
            styles.change,
            { color: stockData.change >= 0 ? '#FF5B5B' : '#4A90E2' },
          ]}
        >
          {stockData.change > 0
            ? `+${stockData.change}%`
            : `${stockData.change}%`}
        </Text>
      </View>

      {/* 🔹 각 항목을 카드로 표시 */}
      {infoItems.map((item, index) => (
        <View key={index} style={styles.card}>
          <Text style={styles.cardLabel}>{item.label}</Text>
          <Text style={styles.cardValue}>{item.value}</Text>
        </View>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#161B2E',
    padding: 20,
  },
  center: {
    flex: 1,
    backgroundColor: '#161B2E',
    justifyContent: 'center',
    alignItems: 'center',
  },
  title: {
    fontSize: 26,
    fontWeight: '700',
    color: '#fff',
    marginBottom: 8,
  },
  priceRow: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    marginBottom: 20,
  },
  price: {
    fontSize: 32,
    color: '#fff',
    fontWeight: '700',
  },
  change: {
    fontSize: 18,
    marginLeft: 10,
    fontWeight: '600',
  },
  // 🔹 카드 스타일
  card: {
    backgroundColor: '#1E2336',
    borderRadius: 16,
    paddingVertical: 16,
    paddingHorizontal: 20,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 3,
  },
  cardLabel: {
    color: '#B0B3C2',
    fontSize: 15,
    marginBottom: 6,
  },
  cardValue: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: '600',
  },
});
