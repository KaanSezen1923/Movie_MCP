import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert, ActivityIndicator } from 'react-native';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const AuthScreen = ({ onLoginSuccess }: { onLoginSuccess: (id: number, name: string) => void }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleAuth = async () => {
    if (!username || !password || (!isLogin && !email)) {
      Alert.alert("Hata", "Lütfen tüm alanları doldurun.");
      return;
    }

    setLoading(true);
    const endpoint = isLogin ? '/login' : '/signup';
    const payload = isLogin ? { username, password } : { username, email, password };

    try {
      const response = await axios.post(`${API_BASE_URL}${endpoint}`, payload);
      if (isLogin) {
        // Backend'den gelen user_id ve username'i üst bileşene gönder
        onLoginSuccess(response.data.user_id, response.data.username);
      } else {
        Alert.alert("Başarılı", "Kayıt olundu, şimdi giriş yapabilirsiniz.");
        setIsLogin(true);
      }
    } catch (error: any) {
      Alert.alert("Hata", error.response?.data?.detail || "Bir sorun oluştu.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.authContainer}>
      <Text style={styles.title}>{isLogin ? 'Giriş Yap' : 'Kayıt Ol'}</Text>
      <TextInput 
        style={styles.input} 
        placeholder="Kullanıcı Adı" 
        placeholderTextColor="#999"
        value={username}
        onChangeText={setUsername}
      />
      {!isLogin && (
        <TextInput 
          style={styles.input} 
          placeholder="E-posta" 
          placeholderTextColor="#999"
          value={email}
          onChangeText={setEmail}
          keyboardType="email-address"
        />
      )}
      <TextInput 
        style={styles.input} 
        placeholder="Şifre" 
        placeholderTextColor="#999"
        secureTextEntry 
        value={password}
        onChangeText={setPassword}
      />
      <TouchableOpacity style={styles.button} onPress={handleAuth} disabled={loading}>
        {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.buttonText}>{isLogin ? 'Giriş' : 'Kayıt Ol'}</Text>}
      </TouchableOpacity>
      <TouchableOpacity onPress={() => setIsLogin(!isLogin)}>
        <Text style={styles.switchText}>
          {isLogin ? 'Hesabınız yok mu? Kayıt olun' : 'Zaten hesabınız var mı? Giriş yapın'}
        </Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  // ... Mevcut chat stilleriniz ...
  authContainer: {
    flex: 1,
    backgroundColor: '#121212',
    justifyContent: 'center',
    padding: 20,
  },
  title: {
    color: '#fff',
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 30,
    textAlign: 'center',
  },
  input: {
    backgroundColor: '#2C2C2C',
    borderRadius: 8,
    padding: 15,
    color: '#fff',
    marginBottom: 15,
    fontSize: 16,
  },
  button: {
    backgroundColor: '#E50914',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 10,
  },
  buttonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  switchText: {
    color: '#999',
    textAlign: 'center',
    marginTop: 20,
  },
});

export default AuthScreen;