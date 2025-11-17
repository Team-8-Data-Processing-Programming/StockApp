import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { useNavigation } from '@react-navigation/native';

export default function StockCard({ stock, rank }) {
  const navigation = useNavigation();

  if (!stock) return null;

  const getMedalEmoji = (rank) => {
    if (rank === 1) return '🥇';
    if (rank === 2) return '🥈';
    if (rank === 3) return '🥉';
    return rank; // 4등 이후는 숫자로 표시
  };

  // 🔹 카드 클릭 시 상세 화면으로 이동
  const handlePress = () => {
    navigation.navigate('StockDetail', {
      stockName: stock.name,
      ticker: stock.ticker || stock.id,
    });
  };

  const num = (v, d = 0) => {
    const n = Number(v ?? 0);
    if (Number.isNaN(n)) return String(v ?? '');
    return n.toLocaleString(undefined, {
      minimumFractionDigits: 0,
      maximumFractionDigits: d,
    });
  };

  const changeValue = Number(stock?.change ?? 0);
  const hasChange = stock?.change !== null && stock?.change !== undefined;
  const isUp = changeValue > 0;
  const isDown = changeValue < 0;

  const changeText = hasChange
    ? `${isUp ? '+' : ''}${changeValue.toFixed(2)}%`
    : '-';

  const changeColor = hasChange ? (isUp ? '#FF5B5B' : '#4A90E2') : '#B0B3C2';

  return (
    <TouchableOpacity onPress={handlePress} activeOpacity={0.85}>
      <View style={styles.card}>
        <View style={styles.rankBox}>
          <Text style={styles.rankText}>{getMedalEmoji(rank)}</Text>
        </View>
        <View style={styles.infoBox}>
          <Text style={styles.name}>{stock?.name}</Text>

          <Text style={styles.price}>{num(stock?.price)}원</Text>

          <Text style={[styles.rate, { color: changeColor }]}>
            {changeText}
          </Text>
        </View>
      </View>
    </TouchableOpacity>
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
    alignSelf: 'flex-start',
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
  rankText: { color: '#153fe4ff', fontWeight: '700', fontSize: 16 },
  infoBox: { flex: 1 },
  name: { color: '#FFFFFF', fontSize: 18, fontWeight: '600' },
  price: { color: '#B0B3C2', fontSize: 15, marginTop: 4 },
  rate: { marginTop: 4, fontSize: 14, fontWeight: '500' },
});
