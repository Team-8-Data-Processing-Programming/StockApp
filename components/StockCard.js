import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { useNavigation } from '@react-navigation/native';

export default function StockCard({ stock, rank }) {
  const navigation = useNavigation();

  if (!stock) return null;

  // 🔹 카드 클릭 시 상세 화면으로 이동
  const handlePress = () => {
    navigation.navigate('StockDetail', {
      stockName: stock.name,
      ticker: stock.id, // ✅ 여기가 바로 종목코드
    });
  };

  // 퍼센트로 칠해줄 기준: unit === '%' 이거나 라벨이 '배당수익률'/'상승률'
  const isPercent =
    stock?.unit === '%' ||
    stock?.metricLabel === '배당수익률' ||
    stock?.metricLabel === '상승률';

  const valNum = Number(stock?.change ?? 0);
  const isUp = isPercent ? valNum > 0 : false;

  const num = (v, d = 0) =>
    Number(v ?? 0).toLocaleString(undefined, { maximumFractionDigits: d });

  let metricText = '';
  switch (stock?.metricLabel) {
    case '상승률':
      metricText = `${valNum > 0 ? '+' : ''}${valNum.toFixed(2)}%`;
      break;
    case '거래량증가율':
      metricText = `+${valNum.toFixed(2)}%`;
      break;
    case '변동성':
      metricText = `20일 변동성 ${valNum.toFixed(2)}%`;
      break;
    case '거래량':
      metricText = `거래량 ${num(stock?.value)}주`;
      break;
    case '거래대금':
      metricText = `거래대금 ${num(stock?.value)}원`;
      break;
    case '배당수익률':
      metricText = `배당수익률 ${valNum.toFixed(2)}%`;
      break;
    case 'PER':
      metricText = `PER ${valNum.toFixed(2)}`;
      break;
    case 'PBR':
      metricText = `PBR ${valNum.toFixed(2)}`;
      break;
    default:
      metricText = String(stock?.change ?? '');
  }

  return (
    <TouchableOpacity onPress={handlePress} activeOpacity={0.85}>
      <View style={styles.card}>
        <View style={styles.rankBox}>
          <Text style={styles.rankText}>{rank}</Text>
        </View>
        <View style={styles.infoBox}>
          <Text style={styles.name}>{stock?.name}</Text>
          <Text style={styles.price}>{num(stock?.price)}원</Text>
          <Text
            style={[
              styles.rate,
              isPercent
                ? { color: isUp ? '#FF5B5B' : '#4A90E2' }
                : { color: '#B0B3C2' },
            ]}
          >
            {metricText}
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
