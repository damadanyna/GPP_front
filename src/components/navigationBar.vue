<template>
  <v-card>
    <v-layout>
          <v-navigation-drawer v-model="drawer" :rail="rail" permanent @click="rail = false">
              <v-list-item prepend-avatar="https://randomuser.me/api/portraits/men/85.jpg" title="John Leider" nav>
                  <template v-slot:append>
                      <v-btn icon="mdi-chevron-left" variant="text" @click.stop="rail = !rail"></v-btn>
                  </template>
              </v-list-item>
              <div>
                <i class=""></i>
              </div>
              <v-divider></v-divider>

              <v-list density="compact" nav>
                  <v-list-item prepend-icon="mdi-home-city" title="Home" value="home" to="/home_page"></v-list-item>
                  <v-list-item prepend-icon="mdi-account" title="My Account" value="account"></v-list-item>
                  <v-list-item prepend-icon="mdi-account-group-outline" title="Users" value="users"></v-list-item>
              </v-list>
          </v-navigation-drawer>
          <v-main style="height: 100vh">
              <!-- Add router-view here to render your pages -->
              <router-view></router-view>
          </v-main>
      </v-layout>
  </v-card>
</template>

<script>
export default {
  data() {
      return {
          drawer: true,
          rail: true,
      }
  },
}
</script>
