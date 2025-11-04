import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { StatusBar } from 'expo-status-bar'; // ✅ 추가
import HomeScreen from './screens/HomeScreen';

const Stack = createStackNavigator();

export default function App() {
  return (
    <>
      {/* ✅ 상태바 색상 및 스타일 설정 */}
      <StatusBar style="light" backgroundColor="#161B2E" />

      <NavigationContainer>
        <Stack.Navigator
          screenOptions={{
            headerStyle: { backgroundColor: '#161B2E' },
            headerTitleStyle: { color: '#FFFFFF' },
            headerTintColor: '#FFFFFF',
            cardStyle: { backgroundColor: '#161B2E' },
          }}
        >
          <Stack.Screen name="홈" component={HomeScreen} />
        </Stack.Navigator>
      </NavigationContainer>
    </>
  );
}
