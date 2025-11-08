import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function StockCard({ stock, rank }) {
  const isUp = stock.change > 0;

  const getMedalEmoji = (rank) => {
    if (rank === 1) return '🥇';
    if (rank === 2) return '🥈';
    if (rank === 3) return '🥉';
    return rank;
  };
  
  return (
    <View style={styles.card}>
      {/* ✅ 순위 번호 */}
      <View style={styles.rankBox}>
        <Text style={styles.rankText}>{getMedalEmoji(rank)}</Text>
      </View>

      {/* ✅ 주식 정보 */}
      <View style={styles.infoBox}>
        <Text style={styles.name}>{stock.name}</Text>
        <Text style={styles.price}>{stock.price.toLocaleString()}원</Text>
        <Text style={[styles.rate, { color: isUp ? '#FF5B5B' : '#4A90E2' }]}>
          {isUp ? '+' : ''}
          {stock.change}원 ({stock.rate}%)
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: 'row',
    backgroundColor: '#1E2336',
    borderRadius: 14,
    paddingVertical: 14,
    paddingHorizontal: 20,
    marginBottom: 12,
    width: '90%',
    alignSelf: 'flex-start', // ✅ 왼쪽 정렬
    alignItems: 'center',
  },
  rankBox: {
    width: 50,
    height: 50,
    borderRadius: 8,
    backgroundColor: '#161B2E',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  rankText: {
    color: '#153fe4ff', // 황금색 느낌 (순위 강조)
    fontWeight: '700',
    fontSize: 20,
  },
  infoBox: {
    flex: 1,
  },
  name: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: '600',
  },
  price: {
    color: '#B0B3C2',
    fontSize: 15,
    marginTop: 4,
  },
  rate: {
    marginTop: 4,
    fontSize: 14,
    fontWeight: '500',
  },
});
