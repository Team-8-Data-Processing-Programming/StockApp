// screens/WelcomeScreen.js

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Animated,
  Easing,
} from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';

export default function WelcomeScreen({ navigation }) {
  // 애니메이션 값 초기화
  const bounceValue = new Animated.Value(1);

  // 진입 시 애니메이션 실행
  React.useEffect(() => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(bounceValue, {
          toValue: 1.1,
          duration: 600,
          easing: Easing.inOut(Easing.ease),
          useNativeDriver: true,
        }),
        Animated.timing(bounceValue, {
          toValue: 1,
          duration: 600,
          easing: Easing.inOut(Easing.ease),
          useNativeDriver: true,
        }),
      ])
    ).start();
  }, []);

  const handleStart = () => {
    navigation.navigate('홈');
  };

  return (
    <View style={styles.container}>
      {/* 타이틀 */}
      <Text style={styles.title}>오늘의 주식정보가{'\n'}궁금하다면</Text>

      {/* 아이콘 애니메이션 */}
      <Animated.View
        style={[styles.iconBox, { transform: [{ scale: bounceValue }] }]}
      >
        <MaterialIcons name="trending-up" size={64} color="white" />
      </Animated.View>

      {/* 시작 버튼 */}
      <TouchableOpacity style={styles.button} onPress={handleStart}>
        <Text style={styles.buttonText}>시작 하기</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1f2e',
    padding: 24,
    justifyContent: 'center',
    alignItems: 'center',
  },
  title: {
    color: 'white',
    fontSize: 26,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 40,
  },
  iconBox: {
    width: 120,
    height: 120,
    backgroundColor: '#7c3aed',
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#a855f7',
    shadowOpacity: 0.4,
    shadowOffset: { width: 0, height: 10 },
    shadowRadius: 20,
    marginBottom: 60,
  },

  button: {
    backgroundColor: '#7c3aed',
    paddingVertical: 14,
    paddingHorizontal: 32,
    borderRadius: 16,
    shadowColor: '#a855f7',
    shadowOpacity: 0.3,
    shadowRadius: 10,
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
