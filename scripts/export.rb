# frozen_string_literal: true

require "json"

def load_zenn_json(path)
  unless File.file?(path)
    raise ArgumentError, "File not found: #{path}"
  end

  raw = File.read(path, encoding: "UTF-8")
  data = JSON.parse(raw) # => Hash or Array

  unless data.is_a?(Hash)
    raise TypeError, "Expected top-level JSON object (Hash), got: #{data.class}"
  end

  data['articles'].each do |a|
    puts a['tags']
    #puts a['slug']
    #puts a['published_at']
  end
rescue JSON::ParserError => e
  raise JSON::ParserError, "Invalid JSON in #{path}: #{e.message}"
end

load_zenn_json("zenn1.json")
load_zenn_json("zenn2.json")
