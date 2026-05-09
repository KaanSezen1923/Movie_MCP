import React, { useState } from 'react';
import { View, Text, Switch, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { LogOut, Settings, Filter } from 'lucide-react-native';

const Profile = ({ onLogout }: any) => {
  const [onlyNetflix, setOnlyNetflix] = useState(false);
  const [darkMode, setDarkMode] = useState(true);

  return (
    <ScrollView style={styles.container}>
      <View style={styles.profileHeader}>
        <View style={styles.avatar}><Text style={styles.avatarText}>K</Text></View>
        <Text style={styles.username}>Kaan Sezen</Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Tercihler</Text>
        <View style={styles.row}>
          <Text style={styles.rowLabel}>Sadece Netflix İçerikleri</Text>
          <Switch value={onlyNetflix} onValueChange={setOnlyNetflix} trackColor={{ true: '#E50914' }} />
        </View>
        <View style={styles.row}>
          <Text style={styles.rowLabel}>Karanlık Mod</Text>
          <Switch value={darkMode} onValueChange={setDarkMode} trackColor={{ true: '#E50914' }} />
        </View>
      </View>

      <TouchableOpacity style={styles.logoutButton} onPress={onLogout}>
        <LogOut color="#fff" size={20} />
        <Text style={styles.logoutText}>Çıkış Yap</Text>
      </TouchableOpacity>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000', padding: 20 },
  profileHeader: { alignItems: 'center', marginVertical: 30 },
  avatar: { width: 80, height: 80, borderRadius: 40, backgroundColor: '#E50914', justifyContent: 'center', alignItems: 'center' },
  avatarText: { color: '#fff', fontSize: 32, fontWeight: 'bold' },
  username: { color: '#fff', fontSize: 20, fontWeight: 'bold', marginTop: 10 },
  section: { backgroundColor: '#121212', borderRadius: 12, padding: 15, marginBottom: 20 },
  sectionTitle: { color: '#E50914', fontWeight: 'bold', marginBottom: 15, fontSize: 14, textTransform: 'uppercase' },
  row: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 },
  rowLabel: { color: '#fff', fontSize: 16 },
  logoutButton: { flexDirection: 'row', backgroundColor: '#222', padding: 15, borderRadius: 12, justifyContent: 'center', alignItems: 'center', marginTop: 20 },
  logoutText: { color: '#fff', fontWeight: 'bold', marginLeft: 10 }
});

export default Profile;